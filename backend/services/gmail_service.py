from googleapiclient.discovery import build
import re
import html
import asyncio
import base64

class GmailService:
    def _clean_text(self, text):
        if not text: return ""
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html.unescape(text)
        return ' '.join(text.split()).strip()

    def _get_body(self, payload):
        """Recursively search for text/plain or text/html in message payload."""
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data')
                    if data:
                        # Prioritize HTML for full view if available, but for now just append
                        body += base64.urlsafe_b64decode(data).decode('utf-8')
                elif 'parts' in part:
                    body += self._get_body(part)
        else:
            data = payload.get('body', {}).get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        return body

    async def fetch_latest_emails(self, credentials, max_results=10):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_fetch, credentials, max_results)

    def _sync_fetch(self, credentials, max_results):
        service = build('gmail', 'v1', credentials=credentials, cache_discovery=False)
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        email_list = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            headers = msg_data['payload'].get('headers', [])
            subject = "No Subject"
            sender = "Unknown Sender"
            date_str = ""
            
            for header in headers:
                name = header['name'].lower()
                if name == 'subject':
                    subject = header['value']
                elif name == 'from':
                    sender = header['value']
                    if '<' in sender:
                        sender = sender.split('<')[0].strip()
                    sender = sender.replace('"', '')
                elif name == 'date':
                    date_str = header['value']
            
            snippet = html.unescape(msg_data.get('snippet', ''))
            labels = msg_data.get('labelIds', [])
            
            time_display = date_str
            try:
                parts = date_str.split()
                if len(parts) >= 5:
                    time_display = f"{parts[1]} {parts[2]} {parts[4][:5]}"
            except:
                pass
                
            email_list.append({
                'id': msg['id'],
                'threadId': msg['threadId'],
                'sender': sender,
                'subject': subject,
                'snippet': snippet,
                'time': time_display,
                'tags': ['Inbox'] if 'INBOX' in labels else ['Archived'],
                'labels': labels,
                'priority': 'Normal'
            })
            
        return email_list

    async def get_email_detail(self, credentials, message_id):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_get_detail, credentials, message_id)

    def _sync_get_detail(self, credentials, message_id):
        service = build('gmail', 'v1', credentials=credentials, cache_discovery=False)
        msg_data = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        
        headers = msg_data['payload'].get('headers', [])
        subject = ""
        sender = ""
        recipient = ""
        timestamp = ""
        
        for header in headers:
            name = header['name'].lower()
            if name == 'subject': subject = header['value']
            elif name == 'from': sender = header['value']
            elif name == 'to': recipient = header['value']
            elif name == 'date': timestamp = header['value']
            
        body = self._get_body(msg_data['payload'])
        
        return {
            'id': message_id,
            'subject': subject,
            'sender': sender,
            'recipient': recipient,
            'timestamp': timestamp,
            'body': body,
            'snippet': msg_data.get('snippet', ''),
            'labels': msg_data.get('labelIds', [])
        }

gmail_service = GmailService()
