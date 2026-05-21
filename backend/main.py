from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.websocket.manager import manager
from backend.services.auth_service import auth_service
from backend.services.gmail_service import gmail_service
from backend.services.ai_service import ai_service
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "project": settings.project_name}

@app.get("/auth/google/login")
async def google_login():
    logger.info("Starting Google OAuth login flow")
    auth_url, state = auth_service.get_google_auth_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/callback")
async def google_callback(request: Request):
    logger.info("Received Google OAuth callback")
    code = request.query_params.get("code")
    if not code:
        logger.error("No code provided in callback")
        raise HTTPException(status_code=400, detail="Code not provided")
    
    try:
        session_id = auth_service.exchange_code_for_token(code)
        logger.info(f"Successfully exchanged code for token. Session ID created.")
        return RedirectResponse(url=f"{settings.frontend_url}/?token={session_id}")
    except Exception as e:
        logger.error(f"Error exchanging code for token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/emails/latest")
async def get_emails(token: str):
    logger.info("Fetching emails for token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    creds = auth_service.get_credentials(token)
    if not creds:
        logger.warning("Invalid or expired session token")
        raise HTTPException(status_code=401, detail="Invalid token")
        
    try:
        emails = await gmail_service.fetch_latest_emails(creds, max_results=10)
        
        # Add AI Summary to each email concurrently
        async def process_email(email):
            summary = await ai_service.summarize_email(email['snippet'])
            email['ai_summary'] = summary
            return email

        emails_with_ai = await asyncio.gather(*[process_email(e) for e in emails])
        return {"emails": emails_with_ai}
    except Exception as e:
        logger.error(f"Error fetching emails from Gmail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/emails/{message_id}")
async def get_email_detail(message_id: str, token: str):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    creds = auth_service.get_credentials(token)
    if not creds:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    try:
        # 1. Fetch full email content
        detail = await gmail_service.get_email_detail(creds, message_id)
        
        # 2. Process with full AI analysis
        ai_analysis = await ai_service.analyze_email_full(detail['body'] or detail['snippet'])
        detail['ai_analysis'] = ai_analysis
        
        return detail
    except Exception as e:
        logger.error(f"Error fetching email detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_insights(token: str):
    creds = auth_service.get_credentials(token)
    if not creds:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    try:
        emails = await gmail_service.fetch_latest_emails(creds, max_results=3)
        combined_text = " ".join([e['snippet'] for e in emails])
        insight = await ai_service.extract_opportunities(combined_text)
        
        return {
            "insights": [
                {
                    "type": "opportunity",
                    "title": "Inbox Analysis",
                    "desc": insight,
                    "action": "Review Strategy"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return {"insights": []}

@app.websocket("/ws/dashboard_client")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "dashboard_client")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"System Received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard_client")
