import sys
import os
from pathlib import Path

# Ensure the project root is on sys.path and set as current working directory
# This allows imports like 'from utils.otp_utils import ...' and lets
# config/config.yaml and .env be discovered via relative paths used in ConfigManager.
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from utils.otp_utils import fetch_otp_from_email

if __name__ == "__main__":
    """
    A simple script to test the fetch_otp_from_email function in isolation.
    """
    print("🔬 Attempting to fetch OTP from email...")
    print("Ensure an unread OTP email is in the inbox.")

    try:
        # Call the function you want to test
        otp = fetch_otp_from_email()

        if otp:
            print("\n" + "=" * 40)
            print(f"✅ SUCCESS! OTP Found: {otp}")
            print("=" * 40)
        else:
            print("\n" + "=" * 40)
            print("⚠️  Could not find OTP, but no error was raised.")
            print("=" * 40)

    except (TimeoutError, ConnectionError, ValueError) as e:
        # Catch the specific errors your function is designed to raise
        print("\n" + "=" * 40)
        print(f"❌ ERROR: The function failed as expected.")
        print(f"   Reason: {e}")
        print("=" * 40)
    except Exception as e:
        # Catch any other unexpected errors
        print("\n" + "=" * 40)
        print(f"💥 UNEXPECTED ERROR: An unhandled exception occurred.")
        print(f"   Details: {e}")
        print("=" * 40)