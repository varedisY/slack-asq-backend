from fastapi import APIRouter, Request, HTTPException,Response
import gpt
import llama
import qdrant
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()
client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))


@router.post("/slack/events")
async def slack_events(request: Request, response: Response):
    try:
        data = await request.json()

        # Add the header to indicate Slack not to retry
        response.headers['X-Slack-No-Retry'] = '1'

        if 'challenge' in data:
            return data['challenge']

        if 'event' in data:
            event = data['event']
            # Ignoring message edit events
            if event.get('subtype') == 'message_changed':
                logging.info("Ignoring message edit event")
                return {"status": "ignored"}

            # Check if the message is a direct message, not sent by a bot, and not an edit event
            if (
                event.get('type') == 'message' and
                event.get('channel_type') == 'im' and
                'subtype' not in event and
                'bot_id' not in event  # Ignore bot messages
            ):
                channel = event['channel']
                text = event['text']

                try:
                    # Respond early to prevent Slack retries
                    response.status_code = 200
                    response.body = '{"status": "processing"}'
                    
                    # Send "Thinking..." message
                    thinking_message = client.chat_postMessage(channel=channel, text="Thinking...")
                    logging.info("Posted 'Thinking...' message: %s", thinking_message)

                    # Perform the search
                    # TODO: Update collection name as needed
                    search_results = qdrant.find(text, "docs")
                    context = "\n".join(result.payload["document"] for result in search_results)

                    # Generate the AI response
                    ai_response = gpt.generate_response(text, context)

                    # Ensure the response structure is as expected
                    response_text = ai_response.choices[0].message.content if ai_response.choices else "I'm not sure how to respond to that."

                    # Update the "Thinking..." message with the AI response
                    client.chat_update(
                        channel=channel,
                        ts=thinking_message['ts'],
                        text=response_text
                    )
                except SlackApiError as e:
                    logging.error("Error posting or updating message: %s", e.response['error'])
                except KeyError as e:
                    logging.error("Unexpected response structure: %s", e)
                    raise HTTPException(status_code=500, detail="AI response format error")
    except Exception as e:
        logging.error("Error processing Slack event: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"status": "ok"}

