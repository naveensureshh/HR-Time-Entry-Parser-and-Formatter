import os
import requests
import pandas as pd
from msal import ConfidentialClientApplication

# === ENV VARIABLES ===
CLIENT_ID = os.environ.get("GRAPH_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GRAPH_CLIENT_SECRET")
TENANT_ID = os.environ.get("GRAPH_TENANT_ID")

# === AUTH SETUP ===
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# === ONEDRIVE INFO ===
DRIVE_ID = "b!plfEkdTmoE-6_Kan9sawslyO9WJ17sVHgZ7TJjfhU1wnNPcDz9MmT4LLkLBTaLqq"
INPUT_FOLDER_ID = "01POVTN3JUCY62SZZ2YBGLTGAFI6HX7LZS"      # Timesheet
OUTPUT_FOLDER_ID = "01POVTN3JWKRDKVHXD4BH356H2GLRSCWKI"     # Time sheet output

# === AUTHENTICATE ===
print("🔐 Authenticating with Microsoft Graph...")
app = ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
token_response = app.acquire_token_for_client(scopes=SCOPE)

if "access_token" not in token_response:
    raise Exception(f"❌ Failed to authenticate:\n{token_response}")

access_token = token_response["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}
print("✅ Authenticated.")

# === GRAPH HELPERS ===
def list_files(folder_id):
    url = f"{GRAPH_BASE_URL}/drives/{DRIVE_ID}/items/{folder_id}/children"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["value"]

def download_file(item_id, filename):
    url = f"{GRAPH_BASE_URL}/drives/{DRIVE_ID}/items/{item_id}/content"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(response.content)

def upload_file(folder_id, file_path):
    file_name = os.path.basename(file_path)
    url = f"{GRAPH_BASE_URL}/drives/{DRIVE_ID}/items/{folder_id}:/{file_name}:/content"
    with open(file_path, "rb") as f:
        response = requests.put(url, headers=headers, data=f)
    response.raise_for_status()
    return response.json()

def process_timesheet(excel_file, reference_csv):
    df_timesheet = pd.read_excel(excel_file)
    df_reference = pd.read_csv(reference_csv)
    df_merged = pd.merge(df_reference, df_timesheet, on="Name", how="left")
    df_merged["Late"] = df_merged["ClockIn"] > df_merged["StartTime"]
    df_merged[df_merged["Late"] == True].to_csv("lateness_report.csv", index=False)

# === MAIN WORKFLOW ===
print("📂 Scanning input folder for timesheets...")
files = list_files(INPUT_FOLDER_ID)
xlsx_files = [f for f in files if f["name"].endswith(".xlsx")]

if not xlsx_files:
    raise Exception("❌ No .xlsx timesheets found in input folder.")

latest_file = sorted(xlsx_files, key=lambda x: x["lastModifiedDateTime"], reverse=True)[0]
download_file(latest_file["id"], "latest_timesheet.xlsx")
print(f"📥 Downloaded: {latest_file['name']}")

process_timesheet("latest_timesheet.xlsx", "Final_Reference_Sheet.csv")
print("✅ Lateness report generated.")

upload_file(OUTPUT_FOLDER_ID, "lateness_report.csv")
print("📤 Uploaded lateness_report.csv to output folder.")
