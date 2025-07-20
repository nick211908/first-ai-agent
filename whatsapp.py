import google.generativeai as genai
import pywhatkit
import time
import datetime
import re
import json

genai.configure(api_key='')
messages = []
model_name = "gemini-1.5-flash"
model = genai.GenerativeModel(model_name).start_chat(history=messages)

def send_whatsapp_message(phone_number, message, hour=None, minute=None):
    try:
        if hour is not None and minute is not None:
            pywhatkit.sendwhatmsg(phone_number, message, hour, minute, wait_time=10, tab_close=True)
            print(f"Scheduled message to {phone_number} at {hour}:{minute}: {message}")
        else:
            pywhatkit.sendwhatmsg_instantly(phone_number, message)
            print(f"Message sent instantly to {phone_number}: {message}")
    except Exception as e:
        print(f"Failed to send message to {phone_number}: {e}")

def generate_response(text):
    try:
        prompt = f"""Extract phone number, message, and time from this request:\n{text}\nReturn JSON in this format:\n{{\"phone\": \"+911234567890\", \"message\": \"message text\", \"hour\": 15, \"minute\": 30}}"""
        response = model.send_message(prompt)
        # Try to extract JSON from the response
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            try:
                info = json.loads(match.group().replace("'", '"'))
                return info
            except Exception as e:
                print("Error parsing info as JSON:", e)
                return None
        else:
            print("No valid JSON found in model response.")
            return None
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

while True:
    try:
        user_input = input("Enter your request: ")
        if user_input.lower() == "exit":
            break
        info = generate_response(user_input)
        if not info:
            print("Could not extract info from your request. Please try again.")
            continue
        phone = info.get('phone')
        message = info.get('message')
        hour = info.get('hour')
        minute = info.get('minute')
        if phone and message:
            if hour is not None and minute is not None:
                send_whatsapp_message(phone, message, hour, minute)
            else:
                send_whatsapp_message(phone, message)
        else:
            print("Missing phone or message in extracted info.")
    except Exception as e:
        print(f"Error processing input: {e}")
        continue
