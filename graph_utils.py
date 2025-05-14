import os
import requests
from msal import ConfidentialClientApplication
from io import BytesIO

def get_graph_token():
    client_id = os.environ['AZURE_CLIENT_ID']
    client_secret = os.environ['AZURE_CLIENT_SECRET']
    tenant_id = os.environ['AZURE_TENANT_ID']

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    scopes = ["https://graph.microsoft.com/.default"]

    app = ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )

    result = app.acquire_token_for_client(scopes=scopes)
    if "access_token" in result:
        return result['access_token']
    else:
        raise Exception("Could not obtain access token")

def download_file(file_name):
    site_id = os.environ['SHAREPOINT_SITE_ID']
    drive_id = os.environ['DRIVE_ID']
    token = get_graph_token()

    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{file_name}:/content"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise Exception(f"Download failed: {response.status_code} - {response.text}")

def upload_file(file_stream, target_filename):
    site_id = os.environ['SHAREPOINT_SITE_ID']
    drive_id = os.environ['DRIVE_ID']
    token = get_graph_token()

    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{target_filename}:/content"
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.put(url, headers=headers, data=file_stream)

    if response.status_code in (200, 201):
        print(f"✅ Uploaded to SharePoint: {target_filename}")
    else:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")
