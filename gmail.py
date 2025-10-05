import os.path
import base64
import email
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
import pickle
import re
from datetime import datetime
from bs4 import BeautifulSoup

# Scopes for Gmail + Google Sheets
scopes = [
    'https://www.googleapis.com/auth/gmail.readonly',
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = None
spreadsheet_id = '1ylbeDeFFmPx_N6Iiu1EEEDrQJe6ePkqlzLRdX1YOU20'

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", scopes)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            print("Token expired or revoked. Deleting and re-authenticating...")
            os.remove("token.json")
            creds = None

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
        creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

def grabSinceJuly():
    all_messages = {}
    next_page_token = None

    service = build('gmail', 'v1', credentials=creds)

    while True:
        results = service.users().messages().list(
            userId='me',
            q=('subject:(application OR interview OR regret OR "next steps" OR "Applying to") '
            '-subject:"apply now" -subject:"apply for" -subject:"job alert" -subject:"apply to" ' \
            '-from:"finalroundai.com" -from:"dice.com" -from:"zillow.com" -from:"jobright.ai" after:2025/07/21 -from:"algoverse.us" -from:"micro1.ai" -from:"yelp.com"'),
            pageToken=next_page_token
        ).execute()
        
        msgs = results.get('messages', [])
        if not msgs:
            break

        for msg in msgs:
            msg_data = service.users().messages().get(
                userId='me', id=msg['id'], format='full'
            ).execute()

            headers = msg_data['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
            date_header = next((h['value'] for h in headers if h['name'] == 'Date'), "")

            body = ""

            def walk_parts(parts):
                nonlocal body
                for part in parts:
                    mime = part.get("mimeType", "")
                    if part.get("parts"):
                        walk_parts(part["parts"])  # recurse deeper
                    elif mime == "text/plain" and "data" in part.get("body", {}):
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        return
                    elif not body and mime == "text/html" and "data" in part.get("body", {}):
                        html_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html_body, "html.parser")
                        body = soup.get_text()

            payload = msg_data.get("payload", {})
            if "parts" in payload:
                walk_parts(payload["parts"])
            elif "data" in payload.get("body", {}):
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
            else:
                if 'data' in msg_data['payload']['body']:
                    body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode('utf-8')
            
            if date_header:
                try:
                    parsed_date = email.utils.parsedate_to_datetime(date_header)
                except Exception:
                    parsed_date = None
            else:
                parsed_date = None

            all_messages[msg['id']] = {
                "threadId": msg_data["threadId"],
                "subject": subject,
                "sender": sender,
                "body": body,
                "date": parsed_date
            }
        
        next_page_token = results.get('nextPageToken')
        if not next_page_token:
            break

    with open('messages_cache.pkl', 'wb') as f:
        pickle.dump(all_messages, f)
    print(f"Fetched {len(all_messages)} messages with subject, sender, and body.")

grabSinceJuly()
# gc = gspread.authorize(creds)
# spreadsheet = gc.open_by_key(spreadsheet_id)


