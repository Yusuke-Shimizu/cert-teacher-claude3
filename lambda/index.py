import json
import boto3
import os
import pprint
import base64

# Initialize the S3 client
s3_client = boto3.client('s3')

def handler(event, context):
    pprint.pprint("event")
    pprint.pprint(event)

    # Extract the bucket name and key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    pprint.pprint("bucket_name")
    pprint.pprint(bucket_name)
    pprint.pprint("object_key")
    pprint.pprint(object_key)
    
    # Retrieve the image from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    # image_content = response['Body'].read()
    image_content = base64.b64encode(response['Body'].read()).decode('utf8')

    bedrock = boto3.client('bedrock-runtime')
    system_prompt = "必ず日本語で答えてください"
    user_message = {
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_content}},
            {"type": "text", "text": "画像に書いてある問題文と選択肢を抜き出して"}
        ]
    }

    messages = [user_message]
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": messages
        }
    )
    modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
    # modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
    accept = 'application/json'
    contentType = 'application/json'
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    pprint.pprint("response_body")
    pprint.pprint(response_body)
    answer = response_body["content"][0]["text"]
    pprint.pprint("answer")
    pprint.pprint(answer)

    return {
        'statusCode': 200,
        'body': response_body
    }
