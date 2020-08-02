import json
import random
import logging
import urllib3
from urllib.parse import parse_qs

http = urllib3.PoolManager()


def handler(event, context):
    logging.error(event)

    if event["resource"] == "/nickname":
        with open("./wordlists/nicknames.txt") as f:
            nicknames = f.read().splitlines()
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "response_type": "ephemeral",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "plain_text",
                                "text": random.choice(nicknames)
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                            "type": "plain_text",
                                            "text": "Try Again",
                                    },
                                    "value": "try_again",
                                    "action_id": "button"
                                }
                            ]
                        }
                    ]
                })
            }

    if event["resource"] == "/nickname-again":
        payload = json.loads(parse_qs(event['body'])['payload'][0])
        url = payload["response_url"]

        with open("./wordlists/nicknames.txt") as f:
            nicknames = f.read().splitlines()
            http.request(
                'POST',
                url,
                headers={'Content-Type': 'application/json'},
                body=json.dumps({
                    "replace_original": "true",
                    "response_type": "ephemeral",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "plain_text",
                                "text": random.choice(nicknames)
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                            "type": "plain_text",
                                            "text": "Try Again",
                                    },
                                    "value": "try_again",
                                    "action_id": "button"
                                }
                            ]
                        }
                    ]
                }),
            )

            return {
                "statusCode": 200,
                "body": {}
            }

    # Error
    return {
        "statusCode": 500,
        "body": {}
    }
