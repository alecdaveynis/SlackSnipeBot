import os
from flask import Flask, request, jsonify
import json
from slack_sdk import WebClient # type: ignore
from slack_sdk.errors import SlackApiError # type: ignore

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

#create leaderboard
leaderboard: dict[str, int] = {}    

app = Flask(__name__)

@app.route('/api/slack/snipe', methods=['GET'])
def slack_events():
    #data = request.json
    # "@Username"
    # project id: os.environ['SNIPE_PROJECT_ID']
    response = client.conversations_list()
    conversations = response["channels"]
    return json.dumps(conversations), 200
    #channel_id=os.environ['SNIPE_PROJECT_ID']
    channel_id="C07RGCK862C"

    #print(channel_id)
    response = client.conversations_history(channel=channel_id)

    conversation_history = response["messages"]
    return json.dumps(conversation_history), 200

    if 'event' in data:
        event = data['event']
        # Look for messages that contain an image and an @mention
        if event['type'] == 'message' and 'text' in event:
            text = event['text']
            user = event['user']

            if '@' in text:
                # Extract the mentioned user (e.g., @user)
                mentioned_user = text.split('@')[1].strip()

                # Update leaderboard
                leaderboard[mentioned_user] = leaderboard.get(mentioned_user, 0) + 1

                try:
                    response = client.chat_postMessage(
                        channel=event['channel'],
                        text=f"{mentioned_user} has been sniped! Total: {leaderboard[mentioned_user]} snipes."
                    )
                except SlackApiError as e:
                    print(f"Error posting message: {e.response['error']}")

    return jsonify({'status': 'ok'})

@app.route('/api/slack/leaderboard', methods=['POST'])
def leaderboard_command():
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "\n".join([f"{user}: {snipes} snipes" for user, snipes in sorted_leaderboard])

    return jsonify({
        'response_type': 'in_channel',
        'text': f"Sniping Leaderboard:\n{leaderboard_text}"
    })

if __name__ == "__main__":
    app.run(port=3000)
