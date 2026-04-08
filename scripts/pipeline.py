# pipeline.py

import pandas as pd
import requests
import os


GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1PIaSrEvGDyv1HEIsYLGmSbSyVwQ2h149yyp3ww3gHqo/export?format=csv"
OUTPUT_FILE = "Consolidated Monthly Stats.csv"

def load_data():
    print("Loading data from Google Sheets...")
    df = pd.read_csv(GOOGLE_SHEET_CSV)
    return df


def clean_data(df):
    print("Cleaning data...")

    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Implementing Partner": "IP Name",
        "Indicator": "Indicators",
        "Achieved": "Achieved Outputs"
    })

    return df


def select_columns(df):
    print("Selecting relevant columns...")

    required_columns = [
        "Month",
        "Indicators",
        "IP Name",
        "Achieved Outputs",
        "Number training partnerships/collaborations to be established",
        "Number participants to complete vocational skills training",
        "Number certifications to be issued",
        "Number participants to complete work readiness or soft skills training"
    ]

    available_columns = [col for col in required_columns if col in df.columns]
    df = df[available_columns]

    return df


def transform_data(df):
    print("Transforming data...")

    numeric_cols = df.select_dtypes(include=['object']).columns

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    df = df.dropna(how='all')

    return df


def get_access_token():
    url = f"https://login.microsoftonline.com/{os.environ['AZURE_TENANT_ID']}/oauth2/v2.0/token"

    data = {
        "client_id": os.environ["AZURE_CLIENT_ID"],
        "client_secret": os.environ["AZURE_CLIENT_SECRET"],
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }

    r = requests.post(url, data=data)
    token_data = r.json()

    print("TOKEN RESPONSE:", token_data)

    if "access_token" not in token_data:
        raise Exception(f"Token error: {token_data}")

    return token_data["access_token"]

def upload_to_sharepoint(file_path):
    print("Uploading to SharePoint...")

    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }

    # GET SITE
    site_url = "https://graph.microsoft.com/v1.0/sites/thelearningtrust.sharepoint.com:/sites/TheLearningTrust"
    site = requests.get(site_url, headers=headers).json()

    print("SITE:", site)

    site_id = site["id"]

    # GET DRIVE (Documents library)
    drive = requests.get(
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive",
        headers=headers
    ).json()

    print("DRIVE:", drive)

    drive_id = drive["id"]

    file_name = os.path.basename(file_path)

    # IMPORTANT: encode space
    folder_path = "Consolidated%20data"

    upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}/{file_name}:/content"

    print("UPLOAD URL:", upload_url)

    with open(file_path, "rb") as f:
        res = requests.put(upload_url, headers=headers, data=f)

    print("UPLOAD RESPONSE:", res.text)

    if res.status_code in [200, 201]:
        print("Upload successful")
    else:
        raise Exception(f"Upload failed: {res.text}")

def run_pipeline():
    df = load_data()
    df = clean_data(df)
    df = select_columns(df)
    df = transform_data(df)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"File created: {OUTPUT_FILE}")

    # Upload step
    upload_to_sharepoint(OUTPUT_FILE)

    print("Pipeline complete")

# =========================

if __name__ == "__main__":
    run_pipeline()
