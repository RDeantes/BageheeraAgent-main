import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    raw = os.environ.get("GOOGLE_CREDS")

    if not raw:
        raise Exception("❌ Falta GOOGLE_CREDS en Railway")

    creds_dict = json.loads(raw)

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)

    return client.open("CONCENTRADO_EMPLEADOS").sheet1