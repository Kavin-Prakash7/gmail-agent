import google.generativeai as genai
from backend.core.config import settings
import asyncio
import json

class AIService:
    def __init__(self):
        self.model = None
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def summarize_email(self, content: str) -> str:
        if not self.model:
            return "AI Summary unavailable (No API key)"
        if not content or len(content.strip()) == 0:
            return "No content to summarize"
            
        try:
            prompt = f"Summarize the following email snippet into a concise, professional 1-sentence summary. Be brief and direct:\n\n{content}"
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error in summarize_email: {e}")
            return "Failed to generate AI summary."

    async def analyze_email_full(self, content: str) -> dict:
        fallback = {
            "summary": "AI processing unavailable or failed.",
            "category": "Unknown",
            "urgency": "Low",
            "intent": "Unknown",
            "tone": "Neutral",
            "trust_score": 0,
            "confidence_score": 0,
            "smart_tags": [],
            "reasoning": "System was unable to analyze this email.",
            "opportunities": [],
            "action_items": []
        }
        
        if not self.model:
            return fallback
            
        try:
            prompt = f"""
            Analyze the following email content as an elite AI orchestration system.
            Provide a strictly valid JSON response with the following keys:
            
            1. 'summary': A concise 1-2 sentence executive summary of the core message.
            2. 'urgency': One of [Low, Medium, High, Critical].
            3. 'category': One of [Job Opportunity, Collaboration, Sponsorship, Invoice, Security Alert, Spam, Newsletter, Client Lead, Interview, Promotion, Urgent Action, Personal, Other].
            4. 'intent': The precise perceived goal of the sender (e.g. 'Seeking partnership', 'Payment request').
            5. 'tone': Tone of the email (e.g. 'Professional', 'Friendly', 'Aggressive', 'Urgent').
            6. 'trust_score': Integer 0-100 indicating likelihood this is a legitimate, non-spam email.
            7. 'confidence_score': Integer 0-100 indicating your confidence in this analysis.
            8. 'smart_tags': Array of 2-4 highly relevant 1-word tags.
            9. 'reasoning': 1 sentence explaining why you categorized it this way.
            10. 'opportunities': Array of strings describing potential business leads, collaborations, or value extracted.
            11. 'action_items': Array of objects, each containing:
                - 'action': A human-readable action (e.g., 'Draft negotiation reply', 'Add deadline to calendar').
                - 'type': One of [draft_reply, archive, mark_important, reminder, task, calendar, auto_categorize].
                - 'context': Brief context for the action.

            Email Content:
            {content[:4000]}

            Respond ONLY with the raw JSON object, no markdown blocks or backticks.
            """
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()
                
            return json.loads(text)
        except Exception as e:
            print(f"Error in analyze_email_full: {e}")
            return fallback

    async def extract_opportunities(self, content: str) -> str:
        if not self.model:
            return "AI Insights unavailable"
        if not content:
            return "No content"
            
        try:
            prompt = f"Extract business opportunities, leads, or urgent actions from this email content in 2 short sentences:\n\n{content}"
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.model.generate_content, prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error in extract_opportunities: {e}")
            return "Failed to extract insights."

ai_service = AIService()
