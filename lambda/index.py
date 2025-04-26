import json
import os
import urllib.request
import urllib.parse
import re

FASTAPI_INFERENCE_URL = os.environ.get("https://be23-34-91-143-15.ngrok-free.app")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        
        body = json.loads(event['body'])
        message = body.get('message')
        conversation_history = body.get('conversationHistory', [])

        if not FASTAPI_INFERENCE_URL:
            raise ValueError("FASTAPI_INFERENCE_URL environment variable is not set.")

        if message is None:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'message' in the request body."})
            }

        print("Processing message:", message)
        print("FastAPI Inference URL:", FASTAPI_INFERENCE_URL)

        request_data = json.dumps({
            "message": message,
            "conversation_history": conversation_history
        }).encode('utf-8')

        req = urllib.request.Request(FASTAPI_INFERENCE_URL, data=request_data, headers={'Content-Type': 'application/json'}, method='POST')

        with urllib.request.urlopen(req) as res:
            response_body = json.loads(res.read().decode('utf-8'))
            print("FastAPI Response:", json.dumps(response_body))

            assistant_response = response_body.get('response')
            updated_conversation_history = response_body.get('conversationHistory', conversation_history + [{"role": "assistant", "content": assistant_response}])

            if assistant_response is None:
                raise ValueError("FastAPI API response does not contain 'response'.")

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({
                    "success": True,
                    "response": assistant_response,
                    "conversationHistory": updated_conversation_history
                })
            }

    except ValueError as ve:
        print("Value Error:", str(ve))
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(ve)})
        }
    except urllib.error.URLError as e:
        print("URL Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Failed to connect to FastAPI API: {str(e)}"})
        }
    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"success": False, "error": str(error)})
        }

