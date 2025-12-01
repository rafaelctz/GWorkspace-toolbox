from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import json

from services.google_workspace import GoogleWorkspaceService

load_dotenv()

app = FastAPI(
    title="DEA Toolbox API",
    description="Tools for AD administrators to manage SAML and SSO integrations",
    version="1.0.0"
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
google_service: Optional[GoogleWorkspaceService] = None


class StatusResponse(BaseModel):
    authenticated: bool
    admin_email: Optional[str] = None
    domain: Optional[str] = None


class AliasExtractionResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    total_users: Optional[int] = None
    users_with_aliases: Optional[int] = None


@app.get("/")
async def root():
    return {
        "message": "DEA Toolbox API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Check if Google Workspace API is authenticated"""
    global google_service

    if google_service is None or not google_service.is_authenticated():
        return StatusResponse(authenticated=False)

    try:
        info = google_service.get_admin_info()
        return StatusResponse(
            authenticated=True,
            admin_email=info.get("email"),
            domain=info.get("domain")
        )
    except Exception as e:
        return StatusResponse(authenticated=False)


@app.post("/api/auth/upload-credentials")
async def upload_credentials(file: UploadFile = File(...)):
    """Upload Google OAuth or Service Account credentials JSON file"""
    try:
        contents = await file.read()
        credentials_data = json.loads(contents)

        # Validate credentials structure - accept both OAuth and Service Account
        is_oauth = "installed" in credentials_data or "web" in credentials_data
        is_service_account = "type" in credentials_data and credentials_data["type"] == "service_account"

        if not is_oauth and not is_service_account:
            raise HTTPException(
                status_code=400,
                detail="Invalid credentials format. Please upload either an OAuth 2.0 Client ID credential (Desktop app) or a Service Account credential from Google Cloud Console."
            )

        # Save credentials
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        with open(credentials_path, "w") as f:
            json.dump(credentials_data, f)

        return {"message": "Credentials uploaded successfully"}

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON file. Please ensure the file is a valid JSON format downloaded from Google Cloud Console."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading credentials: {str(e)}")


@app.post("/api/auth/authenticate")
async def authenticate():
    """Start OAuth flow and authenticate with Google Workspace"""
    global google_service

    try:
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")

        if not os.path.exists(credentials_path):
            raise HTTPException(
                status_code=400,
                detail="Credentials file not found. Please upload credentials first."
            )

        google_service = GoogleWorkspaceService(credentials_path, token_path)
        google_service.authenticate()

        info = google_service.get_admin_info()

        return {
            "message": "Authentication successful",
            "admin_email": info.get("email"),
            "domain": info.get("domain")
        }

    except FileNotFoundError as e:
        google_service = None
        raise HTTPException(
            status_code=400,
            detail="Credentials file not found. Please upload credentials first."
        )
    except Exception as e:
        # Reset service on failure
        google_service = None

        error_msg = str(e)
        if "invalid_grant" in error_msg.lower():
            error_msg = "Authentication failed. The authorization code or refresh token may be invalid or expired. Please try again."
        elif "access_denied" in error_msg.lower():
            error_msg = "Access denied. You may have cancelled the authorization or don't have sufficient permissions."
        elif "redirect_uri_mismatch" in error_msg.lower():
            error_msg = "OAuth redirect URI mismatch. Please check your Google Cloud Console OAuth configuration."

        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/auth/authenticate-service-account")
async def authenticate_service_account(request: dict):
    """Authenticate using service account with domain-wide delegation"""
    global google_service

    try:
        delegated_email = request.get("delegated_email")
        if not delegated_email:
            raise HTTPException(
                status_code=400,
                detail="Delegated admin email is required for service account authentication"
            )

        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")

        if not os.path.exists(credentials_path):
            raise HTTPException(
                status_code=400,
                detail="Credentials file not found. Please upload service account credentials first."
            )

        google_service = GoogleWorkspaceService(credentials_path, token_path, delegated_email)
        google_service.authenticate_service_account(delegated_email)

        # Get domain from delegated email
        domain = delegated_email.split('@')[1] if '@' in delegated_email else ''

        return {
            "message": "Service account authentication successful",
            "admin_email": delegated_email,
            "domain": domain,
            "auth_type": "service_account"
        }

    except FileNotFoundError as e:
        google_service = None
        raise HTTPException(
            status_code=400,
            detail="Service account credentials file not found. Please upload credentials first."
        )
    except Exception as e:
        # Reset service on failure
        google_service = None

        error_msg = str(e)
        if "domain-wide delegation" in error_msg.lower() or "delegated" in error_msg.lower():
            error_msg = "Service account authentication failed. Make sure domain-wide delegation is enabled for this service account in your Google Workspace Admin Console."

        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/auth/credential-type")
async def get_credential_type():
    """Detect the type of uploaded credentials"""
    try:
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")

        if not os.path.exists(credentials_path):
            return {"type": None, "exists": False}

        with open(credentials_path, 'r') as f:
            import json
            cred_data = json.load(f)

            if 'type' in cred_data and cred_data['type'] == 'service_account':
                return {
                    "type": "service_account",
                    "exists": True,
                    "service_account_email": cred_data.get('client_email', '')
                }
            elif 'installed' in cred_data or 'web' in cred_data:
                return {
                    "type": "oauth",
                    "exists": True
                }
            else:
                return {
                    "type": "unknown",
                    "exists": True
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/logout")
async def logout():
    """Logout and clear authentication"""
    global google_service

    try:
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")
        if os.path.exists(token_path):
            os.remove(token_path)

        google_service = None

        return {"message": "Logged out successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/auth/credentials")
async def delete_credentials():
    """Delete uploaded credentials file"""
    global google_service

    try:
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")

        # Remove both files if they exist
        if os.path.exists(credentials_path):
            os.remove(credentials_path)

        if os.path.exists(token_path):
            os.remove(token_path)

        # Reset service
        google_service = None

        return {"message": "Credentials deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/credentials-status")
async def credentials_status():
    """Check if credentials file exists"""
    try:
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        exists = os.path.exists(credentials_path)

        return {
            "exists": exists,
            "path": credentials_path if exists else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tools/extract-aliases", response_model=AliasExtractionResponse)
async def extract_aliases():
    """Extract all users with aliases from Google Workspace"""
    global google_service

    if google_service is None or not google_service.is_authenticated():
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please authenticate first."
        )

    try:
        result = google_service.extract_aliases_to_csv()

        return AliasExtractionResponse(
            success=True,
            message="Aliases extracted successfully",
            file_path=result["file_path"],
            total_users=result["total_users"],
            users_with_aliases=result["users_with_aliases"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools/download-aliases")
async def download_aliases(file_path: str):
    """Download the generated CSV file"""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="text/csv"
    )




if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
