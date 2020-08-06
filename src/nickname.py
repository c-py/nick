import json
import os
import random
import logging
import hmac
import time
import urllib3
from urllib.parse import parse_qs
from hashlib import sha256

http = urllib3.PoolManager()


def validate(event):
    if "X-Slack-Request-Timestamp" not in event["headers"] or "X-Slack-Signature" not in event["headers"]:
        return False

    timestamp = int(event["headers"]["X-Slack-Request-Timestamp"])
    if timestamp < (time.time() - 300):
        return False

    raw_signature = f"""v0:{timestamp}:{event["body"]}"""
    signature_hmac = hmac.new(
        os.environ["SLACK_SIGNING_SECRET"].encode(),
        raw_signature.encode(),
        sha256
    )

    signature = f"v0={signature_hmac.hexdigest()}".encode()
    encoded_header = event["headers"]["X-Slack-Signature"].encode()

    if not hmac.compare_digest(signature, encoded_header):

        return False
    return True


def error():
    return {
        "statusCode": 500,
        "body": json.dumps({
            "message": "Internal Server Error."
        })
    }


def success():
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Success."
        })
    }


def handler(event, context):
    if event["resource"] == "/auth":
        if "code" not in event["queryStringParameters"]:
            return error()

        code = event["queryStringParameters"]["code"]
        r = http.request_encode_body(
            'POST',
            "https://slack.com/api/oauth.v2.access",
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            fields={
                "code": "code",
                "client_id": os.environ["SLACK_CLIENT_ID"],
                "client_secret": os.environ["SLACK_CLIENT_SECRET"]
            }
        )

        if r.status == 200:
            return success()

    if event["resource"] == "/nickname":
        if not validate(event):
            return error()

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
        if not validate(event):
            return error()

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

            return success()

    # Error
    return error()
