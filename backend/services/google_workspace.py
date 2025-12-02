import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',  # Read/Write users
    'https://www.googleapis.com/auth/admin.directory.orgunit.readonly',  # Read OUs
    'https://www.googleapis.com/auth/admin.directory.group'  # Read/Write groups
]


class GoogleWorkspaceService:
    """Service to interact with Google Workspace Admin SDK"""

    def __init__(self, credentials_path: str, token_path: str, delegated_admin_email: Optional[str] = None):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.delegated_admin_email = delegated_admin_email
        self.creds: Optional[Credentials] = None
        self.service = None
        self.auth_type = None  # 'oauth' or 'service_account'

        # Detect credential type
        if os.path.exists(credentials_path):
            with open(credentials_path, 'r') as f:
                cred_data = json.load(f)
                if 'type' in cred_data and cred_data['type'] == 'service_account':
                    self.auth_type = 'service_account'
                elif 'installed' in cred_data or 'web' in cred_data:
                    self.auth_type = 'oauth'

        # Try to load existing OAuth token
        if self.auth_type == 'oauth' and os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            # Refresh if expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                self._save_credentials()

            if self.creds and self.creds.valid:
                self.service = build('admin', 'directory_v1', credentials=self.creds)

        # Auto-authenticate with service account if available
        elif self.auth_type == 'service_account' and delegated_admin_email:
            self.authenticate_service_account(delegated_admin_email)

    def _save_credentials(self):
        """Save credentials to token file"""
        with open(self.token_path, 'w') as token:
            token.write(self.creds.to_json())

    def authenticate(self):
        """Perform OAuth authentication flow"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, SCOPES
            )
            # Use run_local_server with timeout and better error handling
            self.creds = flow.run_local_server(
                port=0,
                authorization_prompt_message='Please visit this URL to authorize: {url}',
                success_message='Authentication successful! You can close this window.',
                open_browser=True
            )
            self._save_credentials()

            self.service = build('admin', 'directory_v1', credentials=self.creds)
            self.auth_type = 'oauth'

        except Exception as e:
            # Clean up on failure
            self.creds = None
            self.service = None
            raise Exception(f"Authentication failed: {str(e)}")

    def authenticate_service_account(self, delegated_admin_email: str):
        """Authenticate using service account with domain-wide delegation"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")

        try:
            # Load service account credentials
            self.creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )

            # Delegate to admin user
            self.creds = self.creds.with_subject(delegated_admin_email)
            self.delegated_admin_email = delegated_admin_email

            # Build service
            self.service = build('admin', 'directory_v1', credentials=self.creds)
            self.auth_type = 'service_account'

        except Exception as e:
            # Clean up on failure
            self.creds = None
            self.service = None
            raise Exception(f"Service account authentication failed: {str(e)}")

    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        if self.creds is None or self.service is None:
            return False

        # Service account credentials are always valid once created
        if self.auth_type == 'service_account':
            return True

        # OAuth credentials need to check validity
        return self.creds.valid

    def get_admin_info(self) -> Dict[str, str]:
        """Get information about the authenticated admin"""
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            # For service accounts, use the delegated admin email
            if self.auth_type == 'service_account':
                email = self.delegated_admin_email
                domain = email.split('@')[1] if email and '@' in email else ''
                return {
                    "email": email,
                    "domain": domain
                }

            # Get email from OAuth credentials
            # The credentials object contains the token info
            import json

            # Try to get email from token
            email = None

            # Check if we have token info with email
            if hasattr(self.creds, 'id_token'):
                import jwt
                decoded = jwt.decode(self.creds.id_token, options={"verify_signature": False})
                email = decoded.get('email')

            # If no email from token, try to get from token file
            if not email and os.path.exists(self.token_path):
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
                    # Some token formats include email
                    email = token_data.get('email') or token_data.get('account', '')

            # If still no email, we need to list users and get the first admin
            # This is a fallback - not ideal but works
            if not email:
                try:
                    # Get the customer ID first
                    results = self.service.users().list(
                        customer='my_customer',
                        maxResults=1,
                        orderBy='email'
                    ).execute()

                    users = results.get('users', [])
                    if users:
                        # Use the domain from the first user
                        first_user_email = users[0].get('primaryEmail', '')
                        domain = first_user_email.split('@')[1] if '@' in first_user_email else ''

                        return {
                            "email": "Authenticated Admin",
                            "domain": domain
                        }
                except:
                    pass

                return {
                    "email": "Authenticated Admin",
                    "domain": "Unknown"
                }

            domain = email.split('@')[1] if email and '@' in email else ''

            return {
                "email": email,
                "domain": domain
            }

        except Exception as error:
            # Fallback - just confirm we're authenticated without email
            return {
                "email": "Authenticated Admin",
                "domain": "Connected"
            }

    def get_all_users(self) -> List[Dict]:
        """Retrieve all users from Google Workspace"""
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        users = []
        page_token = None
        max_results = int(os.getenv("MAX_RESULTS_PER_PAGE", 500))

        try:
            while True:
                results = self.service.users().list(
                    customer='my_customer',
                    maxResults=max_results,
                    orderBy='email',
                    pageToken=page_token
                ).execute()

                users.extend(results.get('users', []))

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            return users

        except HttpError as error:
            raise Exception(f"Failed to retrieve users: {error}")

    def extract_aliases_to_csv(self) -> Dict:
        """Extract all users with aliases and save to CSV"""
        users = self.get_all_users()

        # Prepare data
        users_with_aliases = []
        max_aliases = 0

        for user in users:
            primary_email = user.get('primaryEmail', '')
            aliases = user.get('aliases', [])

            if aliases:  # Only include users with aliases
                user_data = {
                    'primary_email': primary_email,
                    'aliases': aliases
                }
                users_with_aliases.append(user_data)
                max_aliases = max(max_aliases, len(aliases))

        # Create exports directory if it doesn't exist
        exports_dir = './exports'
        os.makedirs(exports_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'google_workspace_aliases_{timestamp}.csv'
        file_path = os.path.join(exports_dir, filename)

        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Create headers
            headers = ['Current Email'] + [f'Alias {i+1}' for i in range(max_aliases)]

            writer = csv.writer(csvfile)
            writer.writerow(headers)

            # Write data
            for user_data in users_with_aliases:
                row = [user_data['primary_email']]
                aliases = user_data['aliases']

                # Add aliases
                for i in range(max_aliases):
                    if i < len(aliases):
                        row.append(aliases[i])
                    else:
                        row.append('')

                writer.writerow(row)

        return {
            'file_path': file_path,
            'total_users': len(users),
            'users_with_aliases': len(users_with_aliases),
            'max_aliases': max_aliases
        }

    def extract_aliases_streaming(self, file_path: str, progress_callback=None) -> Dict:
        """
        Extract aliases with streaming CSV writing and progress tracking.
        Suitable for large environments (millions of users).

        Args:
            file_path: Path where CSV should be written
            progress_callback: Optional callback function(total, processed, users_with_aliases)

        Returns:
            Dict with extraction stats
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        import time

        total_users = 0
        users_with_aliases_count = 0
        page_token = None
        max_results = int(os.getenv("MAX_RESULTS_PER_PAGE", 500))
        max_alias_columns = 0

        # Track all users with aliases for dynamic column sizing
        # We'll do two passes: first to determine max aliases, second to write
        # For very large datasets, we could skip this and use a fixed number
        temp_users = []

        try:
            # First pass: collect users and determine max alias count
            print(f"Starting alias extraction (streaming mode)...")

            while True:
                try:
                    results = self.service.users().list(
                        customer='my_customer',
                        maxResults=max_results,
                        orderBy='email',
                        pageToken=page_token
                    ).execute()

                    page_users = results.get('users', [])

                    for user in page_users:
                        total_users += 1
                        aliases = user.get('aliases', [])

                        if aliases:
                            users_with_aliases_count += 1
                            temp_users.append({
                                'email': user.get('primaryEmail', ''),
                                'aliases': aliases
                            })
                            max_alias_columns = max(max_alias_columns, len(aliases))

                        # Progress callback every 100 users
                        if progress_callback and total_users % 100 == 0:
                            progress_callback(total_users, total_users, users_with_aliases_count)

                    page_token = results.get('nextPageToken')
                    if not page_token:
                        break

                    # Rate limiting: 33ms delay between API calls (~30 calls/sec)
                    time.sleep(0.033)

                except HttpError as error:
                    raise Exception(f"Failed to retrieve users: {error}")

            # Final progress update after collection
            if progress_callback:
                progress_callback(total_users, total_users, users_with_aliases_count)

            print(f"Collected {total_users} users, {users_with_aliases_count} with aliases")

            # Second pass: write to CSV
            print(f"Writing to CSV: {file_path}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Create headers
                headers = ['Current Email'] + [f'Alias {i+1}' for i in range(max_alias_columns)]

                writer = csv.writer(csvfile)
                writer.writerow(headers)

                # Write each user
                for user_data in temp_users:
                    row = [user_data['email']]
                    aliases = user_data['aliases']

                    # Add aliases
                    for i in range(max_alias_columns):
                        if i < len(aliases):
                            row.append(aliases[i])
                        else:
                            row.append('')

                    writer.writerow(row)

            print(f"CSV written successfully: {users_with_aliases_count} users with aliases")

            return {
                'file_path': file_path,
                'total_users': total_users,
                'users_with_aliases': users_with_aliases_count,
                'max_aliases': max_alias_columns
            }

        except Exception as error:
            raise Exception(f"Failed to extract aliases: {error}")

    def get_organizational_units(self) -> List[Dict]:
        """Get all organizational units from Google Workspace"""
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            org_units = []
            results = self.service.orgunits().list(
                customerId='my_customer',
                type='all'
            ).execute()

            for org_unit in results.get('organizationUnits', []):
                org_units.append({
                    'name': org_unit.get('name'),
                    'path': org_unit.get('orgUnitPath'),
                    'parent_path': org_unit.get('parentOrgUnitPath'),
                    'description': org_unit.get('description', '')
                })

            return org_units

        except HttpError as error:
            raise Exception(f"Error fetching organizational units: {error}")

    def inject_attribute_to_users(self, ou_paths: List[str], attribute: str, value: str) -> Dict:
        """Inject a custom attribute to users in specified OUs"""
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            # Get all users from specified OUs
            all_user_emails = []
            user_count_limit = 500  # Safety limit to prevent too large operations

            for ou_path in ou_paths:
                # Try to get users directly from the OU using orgUnitPath parameter
                # This is more efficient than listing all users
                page_token = None
                users_found = 0

                while True:
                    try:
                        # Try using query parameter with orgUnitPath
                        # This approach works for some Google Workspace instances
                        params = {
                            'customer': 'my_customer',
                            'maxResults': 100,  # Smaller batches for faster response
                            'projection': 'basic',
                            'query': f'orgUnitPath={ou_path}'  # Try direct OU filtering
                        }
                        if page_token:
                            params['pageToken'] = page_token

                        results = self.service.users().list(**params).execute()

                        # Add all users from the result
                        for user in results.get('users', []):
                            all_user_emails.append(user.get('primaryEmail'))
                            users_found += 1

                            # Safety check
                            if len(all_user_emails) >= user_count_limit:
                                raise Exception(f"User limit reached ({user_count_limit}). Please select a smaller OU or contact support for batch processing.")

                        page_token = results.get('nextPageToken')
                        if not page_token:
                            break

                    except HttpError as e:
                        # If query filtering doesn't work, fall back to listing all users
                        # and filtering client-side (less efficient but works)
                        print(f"Query filtering failed, using client-side filtering: {e}")

                        page_token = None
                        while True:
                            params = {
                                'customer': 'my_customer',
                                'maxResults': 100,
                                'projection': 'basic'
                            }
                            if page_token:
                                params['pageToken'] = page_token

                            results = self.service.users().list(**params).execute()

                            # Filter users by OU path
                            for user in results.get('users', []):
                                user_ou = user.get('orgUnitPath', '')
                                if user_ou == ou_path or user_ou.startswith(ou_path + '/'):
                                    all_user_emails.append(user.get('primaryEmail'))
                                    users_found += 1

                                    if len(all_user_emails) >= user_count_limit:
                                        raise Exception(f"User limit reached ({user_count_limit}). Please select a smaller OU or contact support for batch processing.")

                            page_token = results.get('nextPageToken')
                            if not page_token:
                                break
                        break  # Exit the outer while loop

            if len(all_user_emails) == 0:
                return {
                    'total_users': 0,
                    'updated_count': 0,
                    'failed_count': 0,
                    'errors': ['No users found in the selected organizational units']
                }

            updated_count = 0
            failed_count = 0
            errors = []

            # Update each user with the new attribute
            for user_email in all_user_emails:
                try:
                    # Handle complex organization attributes
                    if attribute in ['title', 'department', 'employeeType', 'costCenter']:
                        # Fetch full user profile to get existing organizations
                        user_full = self.service.users().get(
                            userKey=user_email,
                            projection='full'
                        ).execute()

                        # Get existing organizations or create new one
                        existing_orgs = user_full.get('organizations', [])
                        if not existing_orgs:
                            existing_orgs = [{}]

                        # Update the primary organization (first one)
                        org = existing_orgs[0]

                        # Map attribute to correct field
                        field_mapping = {
                            'title': 'title',
                            'department': 'department',
                            'employeeType': 'type',
                            'costCenter': 'costCenter'
                        }

                        org[field_mapping[attribute]] = value
                        org['primary'] = True

                        update_body = {'organizations': existing_orgs}

                    elif attribute == 'buildingId':
                        # Handle location/building
                        update_body = {
                            'locations': [{
                                'type': 'desk',
                                'area': 'desk',
                                'buildingId': value
                            }]
                        }

                    elif attribute == 'manager':
                        # Handle manager as relation
                        update_body = {
                            'relations': [{
                                'type': 'manager',
                                'value': value
                            }]
                        }

                    else:
                        # For any other standard attribute, use directly
                        update_body = {attribute: value}

                    # Update the user
                    self.service.users().update(
                        userKey=user_email,
                        body=update_body
                    ).execute()

                    updated_count += 1

                except HttpError as error:
                    failed_count += 1
                    error_msg = str(error)
                    if len(error_msg) > 200:
                        error_msg = error_msg[:200] + "..."
                    errors.append(f"{user_email}: {error_msg}")
                except Exception as error:
                    failed_count += 1
                    error_msg = str(error)
                    if len(error_msg) > 200:
                        error_msg = error_msg[:200] + "..."
                    errors.append(f"{user_email}: {error_msg}")

            return {
                'total_users': len(all_user_emails),
                'updated_count': updated_count,
                'failed_count': failed_count,
                'errors': errors[:10]  # Limit to first 10 errors
            }

        except HttpError as error:
            raise Exception(f"Error injecting attribute: {error}")
        except Exception as error:
            raise Exception(f"Error injecting attribute: {error}")

    def create_group(self, group_email: str, group_name: str, description: str = '') -> Dict:
        """
        Create a new Google Group

        Args:
            group_email: Email address for the group (e.g., sales@domain.com)
            group_name: Display name for the group
            description: Description of the group

        Returns:
            Dict with group information

        Raises:
            Exception if group creation fails
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            group_body = {
                'email': group_email,
                'name': group_name,
                'description': description
            }

            result = self.service.groups().insert(body=group_body).execute()
            print(f"[GoogleWorkspaceService] Created group: {group_email}")
            return result

        except HttpError as error:
            if error.resp.status == 409:
                print(f"[GoogleWorkspaceService] Group already exists: {group_email}")
                return self.get_group(group_email)
            raise Exception(f"Failed to create group: {error}")
        except Exception as error:
            raise Exception(f"Failed to create group: {error}")

    def get_group(self, group_email: str) -> Optional[Dict]:
        """
        Get a Google Group by email

        Args:
            group_email: Email address of the group

        Returns:
            Dict with group information or None if not found
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            result = self.service.groups().get(groupKey=group_email).execute()
            return result
        except HttpError as error:
            if error.resp.status == 404:
                return None
            raise Exception(f"Failed to get group: {error}")
        except Exception as error:
            raise Exception(f"Failed to get group: {error}")

    def add_group_member(self, group_email: str, member_email: str, role: str = 'MEMBER') -> Dict:
        """
        Add a member to a Google Group

        Args:
            group_email: Email address of the group
            member_email: Email address of the member to add
            role: Role of the member ('MEMBER', 'MANAGER', 'OWNER')

        Returns:
            Dict with member information

        Raises:
            Exception if adding member fails
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            member_body = {
                'email': member_email,
                'role': role
            }

            result = self.service.members().insert(
                groupKey=group_email,
                body=member_body
            ).execute()

            return result

        except HttpError as error:
            if error.resp.status == 409:
                # Member already exists
                print(f"[GoogleWorkspaceService] Member already exists: {member_email} in {group_email}")
                return {'email': member_email, 'status': 'already_exists'}
            raise Exception(f"Failed to add member: {error}")
        except Exception as error:
            raise Exception(f"Failed to add member: {error}")

    def get_group_members(self, group_email: str) -> List[str]:
        """
        Get all members of a Google Group

        Args:
            group_email: Email address of the group

        Returns:
            List of member email addresses
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            members = []
            page_token = None

            while True:
                params = {'groupKey': group_email}
                if page_token:
                    params['pageToken'] = page_token

                result = self.service.members().list(**params).execute()

                for member in result.get('members', []):
                    members.append(member.get('email'))

                page_token = result.get('nextPageToken')
                if not page_token:
                    break

            return members

        except HttpError as error:
            if error.resp.status == 404:
                return []
            raise Exception(f"Failed to get group members: {error}")
        except Exception as error:
            raise Exception(f"Failed to get group members: {error}")

    def remove_group_member(self, group_email: str, member_email: str) -> Dict:
        """
        Remove a member from a Google Group

        Args:
            group_email: Email address of the group
            member_email: Email address of the member to remove

        Returns:
            Dict with removal status

        Raises:
            Exception if removing member fails
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            self.service.members().delete(
                groupKey=group_email,
                memberKey=member_email
            ).execute()

            print(f"[GoogleWorkspaceService] Removed member: {member_email} from {group_email}")
            return {'email': member_email, 'status': 'removed'}

        except HttpError as error:
            if error.resp.status == 404:
                # Member doesn't exist in group
                print(f"[GoogleWorkspaceService] Member not found: {member_email} in {group_email}")
                return {'email': member_email, 'status': 'not_found'}
            raise Exception(f"Failed to remove member: {error}")
        except Exception as error:
            raise Exception(f"Failed to remove member: {error}")

    def get_users_in_ou(self, ou_path: str) -> List[Dict]:
        """
        Get all users in a specific Organizational Unit

        Args:
            ou_path: Path to the organizational unit (e.g., /Sales)

        Returns:
            List of dicts with user information (email, name, orgUnitPath)
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated")

        try:
            users = []
            page_token = None

            while True:
                params = {
                    'customer': 'my_customer',
                    'maxResults': int(os.getenv("MAX_RESULTS_PER_PAGE", 500)),
                    'projection': 'basic',
                    'query': f"orgUnitPath='{ou_path}'"
                }
                if page_token:
                    params['pageToken'] = page_token

                result = self.service.users().list(**params).execute()

                for user in result.get('users', []):
                    # Only include users directly in this OU or its sub-OUs
                    user_ou = user.get('orgUnitPath', '')
                    if user_ou == ou_path or user_ou.startswith(ou_path + '/'):
                        users.append({
                            'email': user.get('primaryEmail'),
                            'name': user.get('name', {}).get('fullName', ''),
                            'orgUnitPath': user_ou
                        })

                page_token = result.get('nextPageToken')
                if not page_token:
                    break

            return users

        except HttpError as error:
            raise Exception(f"Failed to get users in OU: {error}")
        except Exception as error:
            raise Exception(f"Failed to get users in OU: {error}")
