import os
import requests
from msal import ConfidentialClientApplication
from io import BytesIO

def get_graph_token():
    client_id     = os.environ['AZURE_CLIENT_ID']
    client_secret = os.environ['AZURE_CLIENT_SECRET']
    tenant_id     = os.environ['AZURE_TENANT_ID']

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )

    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in result:
        return result["access_token"]
    raise Exception("Failed to obtain access token: " + str(result))

def download_file(file_name: str) -> BytesIO:
    """
    Downloads a file by name from the root of the drive.
    """
    drive_id = os.environ["DRIVE_ID"]
    token    = get_graph_token()

    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{file_name}:/content"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        return BytesIO(resp.content)
    else:
        raise Exception(f"Download failed ({resp.status_code}): {resp.text}")

def upload_file(file_stream: BytesIO, target_filename: str):
    """
    Uploads the given stream to the root of the drive under target_filename.
    """
    drive_id = os.environ["DRIVE_ID"]
    token    = get_graph_token()

    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{target_filename}:/content"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.put(url, headers=headers, data=file_stream.getvalue())

    if resp.status_code in (200, 201):
        print(f"✅ Uploaded to Drive: {target_filename}")
    else:
        raise Exception(f"Upload failed ({resp.status_code}): {resp.text}")
