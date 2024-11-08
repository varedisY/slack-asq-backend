from fastapi import APIRouter, Request
import gpt
import llama
import qdrant
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))


@router.post("/slack/events")
async def slack_events(request: Request):
    data = await request.json()
    if 'challenge' in data:
        return data['challenge']
    
    if 'event' in data:
        event = data['event']
        # Check if the message is a direct message and not sent by a bot
        if (
            event.get('type') == 'message' and 
            event.get('channel_type') == 'im' and 
            'subtype' not in event and 
            'bot_id' not in event  # Ignore bot messages
        ):
            channel = event['channel']
            text = event['text']
            try:
                # Send "Thinking..." message
                thinking_message = client.chat_postMessage(channel=channel, text="Thinking...")
                #TODO: UPDATE collectionNAME
                search_results = qdrant.find(text, "docs")

                context = "\n".join(map(lambda result: result.payload["document"], search_results))
                
                ai_response = gpt.generate_response(text, context)

                # Update the "Thinking..." message with the AI response
                client.chat_update(
                    channel=channel,
                    ts=thinking_message['ts'],
                    text=ai_response.choices[0].message.content
                )
            except SlackApiError as e:
                print(f"Error posting message: {e.response['error']}")
    
    return {"status": "ok"}
