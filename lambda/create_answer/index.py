import json
import boto3
import os
import pprint
import base64
from boto3.dynamodb.conditions import Attr

# Initialize the S3 client
s3_client = boto3.client('s3')

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_TABLE_NAME']
table = dynamodb.Table(table_name)

bedrock = boto3.client('bedrock-runtime')

def invoke_model(user_message, system_prompt=None):
    model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    messages = [user_message]
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": messages
    }
    if system_prompt:
        body["system"] = system_prompt
    body = json.dumps(body)
    accept = 'application/json'
    content_type = 'application/json'
    
    # invoke claude3
    response = bedrock.invoke_model(body=body, modelId=model_id, accept=accept, contentType=content_type)
    response_body = json.loads(response.get('body').read())
    response_contents = response_body["content"][0]["text"]
    pprint.pprint("response_contents")
    pprint.pprint(response_contents)
    return response_contents


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

    user_message = {
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_content}},
            {"type": "text", "text": "画像に書いてある問題文と選択肢を抜き出して"}
        ]
    }
    english_question = invoke_model(user_message)
    
    # 和訳
    system_prompt = "必ず日本語で答えてください"
    user_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": f"次の問題文と選択肢をそれぞれ和訳して\n\n-----\n{english_question}"}
        ]
    }
    japanese_question = invoke_model(user_message, system_prompt)
    
    # 解説
    user_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": f"次の問題文と選択肢の解説をしてください\n\n-----\n{japanese_question}"}
        ]
    }
    answer = invoke_model(user_message, system_prompt)

    # DynamoDBにデータを書き込み
    key_id, _ = os.path.splitext(object_key)
    response = table.put_item(
        Item={
            'id': key_id,
            'japanese_question': japanese_question,
            'english_question': english_question,
            'answer': answer,
        }
    )
    
    return {
        'statusCode': 200,
        'body': response
    }
