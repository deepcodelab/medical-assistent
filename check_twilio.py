#!/usr/bin/env python3
"""
Script to check Twilio account for active phone numbers
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TARGET_NUMBER = "+14346615571"

def check_twilio_numbers():
    """Check Twilio account for active phone numbers"""

    print("=" * 60)
    print("TWILIO ACCOUNT CHECK")
    print("=" * 60)

    # Initialize Twilio client
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print(f"✅ Connected to Twilio Account: {TWILIO_ACCOUNT_SID}")
        print()
    except Exception as e:
        print(f"❌ Failed to connect to Twilio: {e}")
        return

    # Fetch all incoming phone numbers
    try:
        print("📞 Fetching your active phone numbers...")
        incoming_phone_numbers = client.incoming_phone_numbers.list()

        if not incoming_phone_numbers:
            print("❌ No phone numbers found in your account!")
            print()
            print("You need to get a phone number:")
            print("👉 https://console.twilio.com/us1/develop/phone-numbers/manage/search")
            return

        print(f"✅ Found {len(incoming_phone_numbers)} phone number(s)")
        print()
        print("-" * 60)

        # List all numbers
        target_found = False
        for idx, number in enumerate(incoming_phone_numbers, 1):
            phone = number.phone_number
            friendly = number.friendly_name
            capabilities = []

            if number.capabilities.get('voice'):
                capabilities.append("Voice")
            if number.capabilities.get('sms'):
                capabilities.append("SMS")
            if number.capabilities.get('mms'):
                capabilities.append("MMS")

            caps_str = ", ".join(capabilities)

            print(f"{idx}. Number: {phone}")
            print(f"   Name: {friendly}")
            print(f"   Capabilities: {caps_str}")
            print(f"   SID: {number.sid}")

            # Check if this is the target number
            if phone == TARGET_NUMBER:
                print(f"   ✅ THIS IS YOUR TARGET NUMBER!")
                target_found = True

            print()

        print("-" * 60)
        print()

        # Result
        if target_found:
            print(f"✅ SUCCESS! {TARGET_NUMBER} is active in your account!")
            print(f"✅ You can use this number for calls.")
        else:
            print(f"❌ {TARGET_NUMBER} is NOT in your account!")
            print()
            print("Your actual Twilio number(s):")
            for number in incoming_phone_numbers:
                print(f"   👉 {number.phone_number}")
            print()
            print("Update your .env and main.py with the correct number above.")

        print()
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error fetching phone numbers: {e}")
        return


if __name__ == "__main__":
    check_twilio_numbers()
