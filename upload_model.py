"""
Upload downloaded model to YOUR Supabase storage.
Usage: python upload_model.py

Run this AFTER download_model_from_friend.py
"""

import os
import sys

# Your own Supabase credentials (from your .env)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

BUCKET_NAME  = "ml-models"
# Change these two lines
FILE_PATH  = "v20260319_171433/vectorizer.joblib"
LOCAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectorizer.joblib")


def upload():
    if not os.path.exists(LOCAL_FILE):
        print(f"❌ model.joblib not found at: {LOCAL_FILE}")
        print("   Run download_model_from_friend.py first.")
        sys.exit(1)

    try:
        from supabase import create_client
    except ImportError:
        print("❌ supabase package not found. Run: pip install supabase")
        sys.exit(1)

    print(f"🔗 Connecting to YOUR Supabase...")
    print(f"   URL    : {settings.supabase_url}")
    print(f"   Bucket : {BUCKET_NAME}")
    print(f"   File   : {FILE_PATH}")

    try:
        client = create_client(settings.supabase_url, settings.supabase_service_key)

        with open(LOCAL_FILE, "rb") as f:
            file_data = f.read()

        size_kb = len(file_data) / 1024
        print(f"\n⬆️  Uploading model ({size_kb:.1f} KB)...")

        client.storage.from_(BUCKET_NAME).upload(
            path=FILE_PATH,
            file=file_data,
            file_options={"content-type": "application/octet-stream"}
        )

        print(f"✅ Model uploaded successfully!")
        print(f"   Bucket : {BUCKET_NAME}")
        print(f"   Path   : {FILE_PATH}")
        print(f"\n👉 Now restart your server: uvicorn app.main:app --reload")
        print("   The 'Bucket not found' error should be gone.")

    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        if "Bucket not found" in str(e):
            print("\n   👉 Create the bucket first:")
            print("      Supabase Dashboard → Storage → New Bucket → 'ml-models'")
        sys.exit(1)


if __name__ == "__main__":
    upload()