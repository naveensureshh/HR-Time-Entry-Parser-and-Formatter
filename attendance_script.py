import os
import requests
from io import BytesIO

# SharePoint / Graph setup
TENANT_ID = os.environ['TENANT_ID']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
SITE_NAME = "BlackmorePartnersNewTimesheet"
SITE_DOMAIN = "blackmorepartners1llc.sharepoint.com"
UPLOAD_FOLDER_ID = "EjZURqqe4-BPvvj6MuMhWUgBlDddKimBWDF89R86Mx2GRQ"
DOWNLOAD_FOLDER_ID = "EjQWPalnOsBMuZgFR49_rzIB6lTKh-1t3HE7akkQs--AVA"

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        'client_id': CLIENT_ID,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()['access_token']


def get_site_id(token):
    url = f"{GRAPH_BASE}/sites/{SITE_DOMAIN}:/sites/{SITE_NAME}"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()['id']


def list_files_in_folder(folder_id, token, site_id):
    url = f"{GRAPH_BASE}/sites/{site_id}/drive/items/{folder_id}/children"
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json().get('value', [])


def download_file(filename):
    token = get_access_token()
    site_id = get_site_id(token)
    files = list_files_in_folder(DOWNLOAD_FOLDER_ID, token, site_id)

    file_meta = next((f for f in files if f['name'].lower() == filename.lower()), None)
    if not file_meta:
        raise FileNotFoundError(f"{filename} not found in folder.")

    download_url = file_meta['@microsoft.graph.downloadUrl']
    r = requests.get(download_url)
    r.raise_for_status()
    return BytesIO(r.content)


def upload_file(file_stream, filename):
    token = get_access_token()
    site_id = get_site_id(token)

    upload_url = f"{GRAPH_BASE}/sites/{site_id}/drive/items/{UPLOAD_FOLDER_ID}:/{filename}:/content"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    r = requests.put(upload_url, headers=headers, data=file_stream.getvalue())
    r.raise_for_status()
    return r.json()
