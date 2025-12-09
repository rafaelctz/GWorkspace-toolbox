#!/usr/bin/env python3
"""
GWorkspace Toolbox - Terminal User Interface (TUI)

A beautiful terminal interface for managing Google Workspace using Textual.
This TUI provides an alternative to the web frontend while using the same backend API.

Usage:
    python tui.py [--backend-url URL]

Options:
    --backend-url URL    Backend API URL (default: http://localhost:8000)
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import httpx
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    Select,
    Static,
    TextArea,
)


# Configuration
BACKEND_URL = "http://localhost:8000"
API_TIMEOUT = 30.0


class APIClient:
    """HTTP client for backend API communication"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=API_TIMEOUT)
        self.auth_token: Optional[str] = None

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    def set_auth_token(self, token: str):
        """Set authentication token for API requests"""
        self.auth_token = token
        self.client.headers["Authorization"] = f"Bearer {token}"

    async def get(self, endpoint: str, **kwargs):
        """GET request to API"""
        url = f"{self.base_url}{endpoint}"
        response = await self.client.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def post(self, endpoint: str, **kwargs):
        """POST request to API"""
        url = f"{self.base_url}{endpoint}"
        response = await self.client.post(url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def health_check(self) -> bool:
        """Check if backend is reachable"""
        try:
            result = await self.get("/")
            return result.get("status") == "running"
        except Exception:
            return False


class WelcomeScreen(Screen):
    """Initial welcome screen with backend connectivity check"""

    CSS = """
    WelcomeScreen {
        align: center middle;
    }

    #welcome-container {
        width: 70;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }

    .title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    .status {
        text-align: center;
        margin: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="welcome-container"):
            yield Label("🚀 GWorkspace Toolbox", classes="title")
            yield Label("Terminal User Interface", classes="subtitle")
            yield Label("Checking backend connection...", id="status", classes="status")
            yield Button("Continue", id="continue-btn", variant="primary", disabled=True)
            yield Button("Quit", id="quit-btn", variant="default")

    async def on_mount(self) -> None:
        """Check backend connectivity on mount"""
        status_label = self.query_one("#status", Label)
        continue_btn = self.query_one("#continue-btn", Button)

        api = self.app.api_client
        is_healthy = await api.health_check()

        if is_healthy:
            status_label.update("✅ Backend connected successfully!")
            status_label.add_class("success")
            continue_btn.disabled = False
        else:
            status_label.update(f"❌ Backend not reachable at {BACKEND_URL}")
            status_label.add_class("error")

    @on(Button.Pressed, "#continue-btn")
    def on_continue(self):
        """Navigate to authentication screen"""
        self.app.push_screen(AuthenticationScreen())

    @on(Button.Pressed, "#quit-btn")
    def on_quit(self):
        """Quit the application"""
        self.app.exit()


class AuthenticationScreen(Screen):
    """Authentication screen for uploading credentials"""

    CSS = """
    AuthenticationScreen {
        align: center middle;
    }

    #auth-container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }

    .title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .section {
        margin: 1 0;
        border: round $primary-darken-2;
        padding: 1;
    }

    Input {
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        import os
        cwd = os.getcwd()

        with Vertical(id="auth-container"):
            yield Label("🔐 Authentication", classes="title")
            yield Label(f"Current directory: {cwd}", classes="subtitle")

            with Vertical(classes="section"):
                yield Label("📄 Upload Credentials JSON:")
                yield Label("Examples: backend/credentials.json  or  ~/Documents/creds.json", classes="subtitle")
                yield Input(
                    placeholder="Path to credentials.json file...",
                    id="credentials-path"
                )
                with Horizontal():
                    yield Button("Upload JSON", id="upload-json-btn", variant="primary")
                    yield Button("Use Default Path", id="use-default-btn", variant="default")

            with Vertical(classes="section"):
                yield Label("🔑 Or use Service Account JSON:")
                yield Label("Service account JSON file with private_key", classes="subtitle")
                yield Input(
                    placeholder="Path to service-account.json file...",
                    id="service-account-path"
                )
                with Horizontal():
                    yield Button("Upload Service Account", id="auth-service-btn", variant="primary")
                    yield Button("Use Default SA Path", id="use-default-sa-btn", variant="default")

            yield Label("", id="auth-status")
            yield Button("Skip (for testing)", id="skip-btn", variant="default")

    @on(Button.Pressed, "#use-default-btn")
    def use_default_path(self):
        """Fill input with default credentials path"""
        path_input = self.query_one("#credentials-path", Input)
        path_input.value = "backend/credentials.json"
        self.notify("Default path filled! Press 'Upload JSON' to continue.")

    @on(Button.Pressed, "#upload-json-btn")
    async def upload_json_credentials(self):
        """Upload JSON credentials file"""
        import os
        status = self.query_one("#auth-status", Label)
        path_input = self.query_one("#credentials-path", Input)

        # Expand ~ to home directory
        path_str = os.path.expanduser(path_input.value.strip())
        path = Path(path_str)

        if not path.exists():
            # Show helpful error with full path attempted
            abs_path = path.resolve()
            status.update(f"❌ File not found: {abs_path}")
            return

        try:
            status.update("⏳ Uploading credentials...")

            with open(path, "rb") as f:
                files = {"file": (path.name, f, "application/json")}
                result = await self.app.api_client.post("/api/auth/upload-credentials", files=files)

            # Backend returns message and credential_type on success (no "success" field)
            if "message" in result and "credential_type" in result:
                status.update(f"✅ {result['message']}")
                await asyncio.sleep(1)
                self.app.push_screen(MainMenuScreen())
            else:
                status.update(f"❌ {result.get('message', 'Authentication failed')}")

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    @on(Button.Pressed, "#use-default-sa-btn")
    def use_default_sa_path(self):
        """Fill input with default service account path"""
        path_input = self.query_one("#service-account-path", Input)
        path_input.value = "backend/service-account.json"
        self.notify("Default SA path filled! Press 'Upload Service Account' to continue.")

    @on(Button.Pressed, "#auth-service-btn")
    async def upload_service_account(self):
        """Upload service account JSON file"""
        import os
        status = self.query_one("#auth-status", Label)
        path_input = self.query_one("#service-account-path", Input)

        # Expand ~ to home directory
        path_str = os.path.expanduser(path_input.value.strip())
        path = Path(path_str)

        if not path.exists():
            # Show helpful error with full path attempted
            abs_path = path.resolve()
            status.update(f"❌ File not found: {abs_path}")
            return

        try:
            status.update("⏳ Uploading service account...")

            with open(path, "rb") as f:
                files = {"file": (path.name, f, "application/json")}
                result = await self.app.api_client.post("/api/auth/upload-credentials", files=files)

            # Backend returns message and credential_type on success (no "success" field)
            if "message" in result and "credential_type" in result:
                status.update(f"✅ {result['message']}")
                await asyncio.sleep(1)
                self.app.push_screen(MainMenuScreen())
            else:
                status.update(f"❌ {result.get('message', 'Authentication failed')}")

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    @on(Button.Pressed, "#skip-btn")
    def skip_auth(self):
        """Skip authentication for testing"""
        self.app.push_screen(MainMenuScreen())


class MainMenuScreen(Screen):
    """Main menu for tool selection"""

    CSS = """
    MainMenuScreen {
        align: center middle;
    }

    #menu-container {
        width: 70;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }

    .title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 2;
    }

    .menu-button {
        width: 100%;
        margin: 1 0;
    }

    .description {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="menu-container"):
            yield Label("🧰 GWorkspace Toolbox", classes="title")
            yield Label("Select a tool:", classes="description")

            yield Button("📧 Alias Extractor", id="alias-extractor", classes="menu-button", variant="primary")
            yield Button("🏷️  Attribute Injector", id="attribute-injector", classes="menu-button", variant="primary")
            yield Button("📊 Batch Jobs Monitor", id="batch-monitor", classes="menu-button", variant="primary")
            yield Button("⚙️  Settings", id="settings", classes="menu-button", variant="default")
            yield Button("🚪 Exit", id="exit", classes="menu-button", variant="error")

    @on(Button.Pressed, "#alias-extractor")
    def open_alias_extractor(self):
        """Open Alias Extractor tool"""
        self.app.push_screen(AliasExtractorScreen())

    @on(Button.Pressed, "#attribute-injector")
    def open_attribute_injector(self):
        """Open Attribute Injector tool"""
        self.app.push_screen(AttributeInjectorScreen())

    @on(Button.Pressed, "#batch-monitor")
    def open_batch_monitor(self):
        """Open Batch Jobs Monitor"""
        self.app.push_screen(BatchMonitorScreen())

    @on(Button.Pressed, "#settings")
    def open_settings(self):
        """Open Settings"""
        self.notify("Settings screen coming soon!")

    @on(Button.Pressed, "#exit")
    def exit_app(self):
        """Exit the application"""
        self.app.exit()


class AliasExtractorScreen(Screen):
    """Screen for extracting user aliases"""

    CSS = """
    AliasExtractorScreen {
        layout: vertical;
    }

    #extractor-container {
        height: 100%;
        padding: 1;
    }

    .title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    DataTable {
        height: 1fr;
        margin: 1 0;
    }

    .controls {
        height: auto;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh_data", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="extractor-container"):
            yield Label("📧 Alias Extractor", classes="title")

            with Horizontal(classes="controls"):
                yield Button("🔄 Extract Aliases", id="extract-btn", variant="primary")
                yield Button("💾 Export to CSV", id="export-btn", variant="success")
                yield Button("🔙 Back", id="back-btn", variant="default")

            yield DataTable(id="aliases-table")
            yield Label("", id="status")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize table on mount"""
        table = self.query_one("#aliases-table", DataTable)
        table.add_columns("Email", "Alias", "Primary")
        table.cursor_type = "row"

    @on(Button.Pressed, "#extract-btn")
    async def extract_aliases(self):
        """Extract aliases from Google Workspace"""
        status = self.query_one("#status", Label)
        table = self.query_one("#aliases-table", DataTable)

        try:
            status.update("⏳ Extracting aliases...")
            table.clear()

            # Call backend API to extract aliases
            result = await self.app.api_client.post("/api/alias-extractor/extract")

            if result.get("success"):
                aliases = result.get("aliases", [])

                for alias in aliases:
                    table.add_row(
                        alias.get("email", ""),
                        alias.get("alias", ""),
                        "✓" if alias.get("is_primary") else ""
                    )

                status.update(f"✅ Extracted {len(aliases)} aliases")
            else:
                status.update(f"❌ {result.get('message', 'Extraction failed')}")

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    @on(Button.Pressed, "#export-btn")
    async def export_to_csv(self):
        """Export aliases to CSV"""
        status = self.query_one("#status", Label)

        try:
            status.update("⏳ Exporting to CSV...")

            result = await self.app.api_client.post("/api/alias-extractor/export")

            if result.get("success"):
                filename = result.get("filename", "aliases.csv")
                status.update(f"✅ Exported to {filename}")
            else:
                status.update(f"❌ {result.get('message', 'Export failed')}")

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    @on(Button.Pressed, "#back-btn")
    def go_back(self):
        """Return to main menu"""
        self.app.pop_screen()


class AttributeInjectorScreen(Screen):
    """Screen for injecting attributes to OUs"""

    CSS = """
    AttributeInjectorScreen {
        layout: vertical;
    }

    #injector-container {
        height: 100%;
        padding: 1;
    }

    .title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .form-section {
        margin: 1 0;
        border: round $primary-darken-2;
        padding: 1;
    }

    TextArea {
        height: 10;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="injector-container"):
            yield Label("🏷️ Attribute Injector", classes="title")

            with Vertical(classes="form-section"):
                yield Label("Organization Unit:")
                yield Input(placeholder="OU path (e.g., /Students)", id="ou-path")

            with Vertical(classes="form-section"):
                yield Label("Attributes (JSON format):")
                yield TextArea(id="attributes-json")

            with Horizontal():
                yield Button("💉 Inject Attributes", id="inject-btn", variant="primary")
                yield Button("🔙 Back", id="back-btn", variant="default")

            yield Label("", id="status")

        yield Footer()

    @on(Button.Pressed, "#inject-btn")
    async def inject_attributes(self):
        """Inject attributes to OU"""
        status = self.query_one("#status", Label)
        ou_input = self.query_one("#ou-path", Input)
        attributes_input = self.query_one("#attributes-json", TextArea)

        try:
            import json

            ou_path = ou_input.value.strip()
            attributes = json.loads(attributes_input.text)

            if not ou_path:
                status.update("❌ Please enter an OU path")
                return

            status.update("⏳ Injecting attributes...")

            result = await self.app.api_client.post(
                "/api/attribute-injector/inject",
                json={"ou_path": ou_path, "attributes": attributes}
            )

            if result.get("success"):
                count = result.get("count", 0)
                status.update(f"✅ Injected attributes to {count} users")
            else:
                status.update(f"❌ {result.get('message', 'Injection failed')}")

        except json.JSONDecodeError:
            status.update("❌ Invalid JSON format")
        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    @on(Button.Pressed, "#back-btn")
    def go_back(self):
        """Return to main menu"""
        self.app.pop_screen()


class BatchMonitorScreen(Screen):
    """Screen for monitoring batch jobs"""

    CSS = """
    BatchMonitorScreen {
        layout: vertical;
    }

    #monitor-container {
        height: 100%;
        padding: 1;
    }

    .title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    DataTable {
        height: 1fr;
        margin: 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh_jobs", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="monitor-container"):
            yield Label("📊 Batch Jobs Monitor", classes="title")

            with Horizontal():
                yield Button("🔄 Refresh", id="refresh-btn", variant="primary")
                yield Button("🔙 Back", id="back-btn", variant="default")

            yield DataTable(id="jobs-table")
            yield Label("", id="status")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize table and load jobs"""
        table = self.query_one("#jobs-table", DataTable)
        table.add_columns("ID", "Tool", "Status", "Progress", "Created")
        table.cursor_type = "row"

        await self.load_jobs()

    async def load_jobs(self):
        """Load batch jobs from API"""
        status = self.query_one("#status", Label)
        table = self.query_one("#jobs-table", DataTable)

        try:
            status.update("⏳ Loading jobs...")
            table.clear()

            result = await self.app.api_client.get("/api/batch-jobs")

            if isinstance(result, list):
                for job in result:
                    table.add_row(
                        str(job.get("id", "")),
                        job.get("tool_name", ""),
                        job.get("status", ""),
                        f"{job.get('progress_percentage', 0):.1f}%",
                        job.get("created_at", "")[:19]
                    )

                status.update(f"✅ Loaded {len(result)} jobs")
            else:
                status.update("❌ Failed to load jobs")

        except Exception as e:
            status.update(f"❌ Error: {str(e)}")

    @on(Button.Pressed, "#refresh-btn")
    async def refresh_jobs(self):
        """Refresh jobs list"""
        await self.load_jobs()

    @on(Button.Pressed, "#back-btn")
    def go_back(self):
        """Return to main menu"""
        self.app.pop_screen()


class GWorkspaceToolboxTUI(App):
    """GWorkspace Toolbox Terminal User Interface"""

    CSS = """
    Screen {
        background: $surface-darken-1;
    }

    .success {
        color: $success;
    }

    .error {
        color: $error;
    }

    .warning {
        color: $warning;
    }
    """

    TITLE = "GWorkspace Toolbox TUI"
    SUB_TITLE = "Terminal interface for Google Workspace management"

    def __init__(self, backend_url: str = BACKEND_URL):
        super().__init__()
        self.api_client = APIClient(backend_url)

    def on_mount(self) -> None:
        """Show welcome screen on app start"""
        self.push_screen(WelcomeScreen())

    async def on_shutdown(self) -> None:
        """Clean up on app shutdown"""
        await self.api_client.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="GWorkspace Toolbox TUI")
    parser.add_argument(
        "--backend-url",
        default=BACKEND_URL,
        help=f"Backend API URL (default: {BACKEND_URL})"
    )

    args = parser.parse_args()

    app = GWorkspaceToolboxTUI(backend_url=args.backend_url)
    app.run()


if __name__ == "__main__":
    main()
