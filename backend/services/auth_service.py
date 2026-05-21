import os
import uuid
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from backend.core.config import settings

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

class AuthService:
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]

    def __init__(self):
        # In-memory session store (session_id -> Credentials)
        self.active_sessions = {}

    def _get_flow(self):
        return Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=settings.google_redirect_uri,
        )

    def get_google_auth_url(self):
        flow = self._get_flow()
        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        return auth_url, state

    def exchange_code_for_token(self, code: str):
        flow = self._get_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = credentials
        return session_id

    def get_credentials(self, session_id: str):
        return self.active_sessions.get(session_id)

auth_service = AuthService()
