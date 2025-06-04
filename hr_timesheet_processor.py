import os
import requests
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SITE_ID = os.getenv("SITE_ID")
DRIVE_ID = os.getenv("DRIVE_ID")
OUTPUT_FOLDER_ID = os.getenv("OUTPUT_FOLDER_ID")

def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def list_recent_csv_file(token):
    url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives/{DRIVE_ID}/root/search(q='.csv')"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    items = response.json().get("value", [])
    if not items:
        print("No .csv files found.")
        return None
    items.sort(key=lambda x: x.get("lastModifiedDateTime", ""), reverse=True)
    return items[0]

def download_file(item, token):
    download_url = item["@microsoft.graph.downloadUrl"]
    filename = item["name"]
    response = requests.get(download_url)
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")
    return filename

def validate_timesheet_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        required_columns = {"Employee ID", "Clock In", "Clock Out"}
        if required_columns.issubset(set(df.columns)):
            return True
        else:
            print(f"❌ CSV file missing required columns: {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error reading CSV file: {file_path}, {e}")
        return False

def process_csv(input_filename):
    output_filename = f"processed_{input_filename}"
    with open(input_filename, "r") as infile, open(output_filename, "w") as outfile:
        for line in infile:
            outfile.write(line)  # placeholder for real processing
    print(f"Processed file saved as: {output_filename}")
    return output_filename

def upload_file(filename, token):
    url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{OUTPUT_FOLDER_ID}:/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    upload_url = f"{url}/{filename}:/content"
    with open(filename, "rb") as f:
        response = requests.put(upload_url, headers={"Authorization": f"Bearer {token}"}, data=f)
    response.raise_for_status()
    print(f"✅ Uploaded file to output folder: {filename}")

if __name__ == "__main__":
    token = get_access_token()
    latest_csv = list_recent_csv_file(token)
    if latest_csv:
        local_file = download_file(latest_csv, token)
        if validate_timesheet_csv(local_file):
            output_file = process_csv(local_file)
            upload_file(output_file, token)
        else:
            print("❌ File validation failed. Skipping processing and upload.")
