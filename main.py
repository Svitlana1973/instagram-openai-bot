from flask import Flask, request
import openai
import os
import requests

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if verify_token == os.getenv("VERIFY_TOKEN"):
            return challenge
        return "Verification token mismatch", 403

    if request.method == 'POST':
        data = request.json
        messaging_event = data.get('entry', [{}])[0].get('messaging', [{}])[0]

        sender_id = messaging_event.get('sender', {}).get('id')
        message_text = messaging_event.get('message', {}).get('text')

        if sender_id and message_text:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": message_text}
                ]
            )
            bot_reply = response.choices[0].message["content"]

            send_instagram_message(sender_id, bot_reply)

        return "EVENT_RECEIVED", 200

    return "Invalid method", 405

def send_instagram_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
