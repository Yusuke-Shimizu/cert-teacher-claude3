import json
import boto3
import os
import logging
import base64

# ロギングの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# S3クライアントの初期化
s3_client = boto3.client('s3')

# DynamoDBの初期化
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_TABLE_NAME']
table = dynamodb.Table(table_name)

# Bedrock-runtimeクライアントの初期化
bedrock = boto3.client('bedrock-runtime')

def invoke_model(user_message, system_prompt=None):
    model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [user_message]
    }
    if system_prompt:
        body["system"] = system_prompt
    response = bedrock.invoke_model(
        body=json.dumps(body),
        modelId=model_id,
        accept='application/json',
        contentType='application/json'
    )
    response_body = json.loads(response.get('body').read())
    response_contents = response_body["content"][0]["text"]
    logger.info("response_contents: %s", response_contents)
    return response_contents

def handler(event, context):
    logger.info("event: %s", event)

    # イベントからバケット名とキーを抽出
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    logger.info("bucket_name: %s, object_key: %s", bucket_name, object_key)
    
    # S3から画像を取得
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    image_content = base64.b64encode(response['Body'].read()).decode('utf8')

    # 英語の質問を取得
    user_message = {
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_content}},
            {"type": "text", "text": "画像に書いてある問題文と選択肢を抜き出して"}
        ]
    }
    english_question = invoke_model(user_message)
    
    # 和訳を取得
    system_prompt = "必ず日本語で答えてください"
    japanese_question = invoke_model(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"次の問題文と選択肢をそれぞれ和訳して\n\n-----\n{english_question}"}
            ]
        },
        system_prompt
    )
    
    # 解説を取得
    answer = invoke_model(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"次の問題文と選択肢の解説をしてください\n\n-----\n{japanese_question}"}
            ]
        },
        system_prompt
    )

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
        'body': json.dumps(response)
    }
