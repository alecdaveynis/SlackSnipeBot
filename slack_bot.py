import requests
import json
import re
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# Slack API Tokens
load_dotenv() 
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
HEADERS = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

# Ensure data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_all_users():
    """Fetch all Slack users and map IDs to names."""
    user_map = {}
    cursor = None  

    while True:
        url = "https://slack.com/api/users.list"
        if cursor:
            url += f"?cursor={cursor}"

        response = requests.get(url, headers=HEADERS)
        data = response.json()

        if data.get("ok"):
            for user in data.get("members", []):
                user_id = user.get("id")
                user_name = (
                    user["profile"].get("display_name") or 
                    user["profile"].get("real_name") or 
                    user.get("name", user_id)
                )
                user_map[user_id] = user_name

            cursor = data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        else:
            print("Error fetching users:", data.get("error"))
            break

    return user_map

def fetch_slack_messages(channel_id):
    """Fetch messages from a Slack channel."""
    url = f"https://slack.com/api/conversations.history?channel={channel_id}&limit=100"
    response = requests.get(url, headers=HEADERS)
    
    data = response.json()
    if not data.get("ok"):
        print(f"Error fetching messages: {data.get('error')}")
    
    return data

def process_messages(channel_id):
    """Process messages and extract snipes."""
    user_map = get_all_users()
    response = fetch_slack_messages(channel_id)
    snipe_logs = []

    if response.get("ok"):
        for message in response.get("messages", []):
            text = message.get("text", "")
            user_id = message.get("user", "UNKNOWN_USER")
            timestamp = message.get("ts", "")

            mentioned_users = re.findall(r"<@([A-Z0-9]+)(?:\|[^>]+)?>", text)

            if user_id == "UNKNOWN_USER":
                continue

            if not mentioned_users:
                continue

            for mentioned_user in mentioned_users:
                sender_name = user_map.get(user_id, "Unknown User")
                target_name = user_map.get(mentioned_user, "Unknown User")

                if sender_name == "Unknown User" or target_name == "Unknown User":
                    continue

                readable_timestamp = datetime.fromtimestamp(float(timestamp)).strftime("%B %d, %Y %I:%M%p")

                snipe_logs.append({
                    "snipe_sender": sender_name,
                    "snipe_target": target_name,
                    "timestamp": readable_timestamp
                })

    # Save to JSON
    json_path = os.path.join(DATA_DIR, "snipe_logs.json")
    with open(json_path, "w") as file:
        json.dump(snipe_logs, file, indent=4)

    # Convert to DataFrame for SQL table format
    df = pd.DataFrame(snipe_logs)

    # Rename columns to match SQL table format
    df.rename(columns={"timestamp": "Time", "snipe_target": "Who got Sniped", "snipe_sender": "Sniper"}, inplace=True)

    # Save to CSV
    csv_path = os.path.join(DATA_DIR, "snipe_logs.csv")
    df.to_csv(csv_path, index=False)

    print(f"Snipe logs saved to '{json_path}' and '{csv_path}'.")

if __name__ == "__main__":
    process_messages(CHANNEL_ID)
