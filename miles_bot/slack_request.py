import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

def configure():
    load_dotenv()


# Flask app to handle Slack events
app = Flask(__name__)




def send_to_openrouter(prompt):
    configure()
    """Send the prompt to OpenRouter.ai and get a response."""
    client = OpenAI(
        base_url=os.getenv('API_URL'),
        api_key=os.getenv('API_KEY'),
    )
    completion = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",  # Specify the model you want to use
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content



@app.route("/slack/events", methods=["POST"])
def slack_events():
    slack_client = WebClient(token=os.getenv('SLACK_TOKEN'))

    """Handle Slack events."""
    data = request.json
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})
    
    if data.get("event", {}).get("type") == "message" and data["event"].get("subtype") is None:
        user_message = data["event"]["text"]
        channel_id = data["event"]["channel"]
        
        # Step 1: Send the message to OpenRouter.ai
        openrouter_response = send_to_openrouter(user_message)
        
        
        # Step 2: Send the final response back to Slack
        try:
            slack_client.chat_postMessage(channel=channel_id, text=openrouter_response)
        except SlackApiError as e:
            print(f"Error posting message: {e.response['error']}")
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=3000)


