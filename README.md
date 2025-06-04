# HR Time Entry Parser and Formatter

This project automates downloading the latest timesheet CSV from a SharePoint drive,
validates the file, performs basic processing and uploads the result back to a
specified folder. The workflow can run manually or on a schedule using GitHub
Actions.

## Requirements
- Python 3.11+
- Access to Microsoft Graph API

## Environment Variables
Create a `.env` file or configure GitHub Actions secrets with the following keys:

- `TENANT_ID` – Azure AD tenant identifier
- `CLIENT_ID` – application (client) ID
- `CLIENT_SECRET` – client secret for the app registration
- `SITE_ID` – SharePoint site ID containing the timesheet files
- `DRIVE_ID` – ID of the drive hosting the files
- `OUTPUT_FOLDER_ID` – ID of the folder where processed files are uploaded

## Local Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set the environment variables listed above.
3. Run the script:
   ```bash
   python hr_timesheet_processor.py
   ```

## GitHub Actions
The provided workflow `.github/workflows/attendance.yml` installs dependencies
and runs the script on a schedule or when triggered manually. Ensure the same
variables are set as repository secrets so the action can authenticate with
Microsoft Graph.
