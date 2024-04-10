import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import os

# ファイルアップロードウィジェットの作成
uploaded_file = st.file_uploader("ファイルを選択してください", type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# DynamoDBにクエリする関数
def query_dynamodb(file_name_without_extension):
    # DynamoDBリソースの作成
    dynamodb = boto3.resource('dynamodb')
    # DynamoDBのテーブル名を指定
    table = dynamodb.Table(table_name)
    
    try:
        # ファイル名（拡張子を除く）を使ってDynamoDBからレコードをクエリ
        response = table.get_item(Key={'id': file_name_without_extension})
        return response.get('Item', None)
    except Exception as e:
        st.error(f"DynamoDBからのクエリ中にエラーが発生しました: {e}")
        return None

# 環境変数からバケット名を取得
bucket_name = os.getenv('BUCKET_NAME')
if bucket_name is None:
    st.error("環境変数'BUCKET_NAME'が設定されていません。")
table_name = os.getenv('DYNAMODB_TABLE_NAME')
if table_name is None:
    st.error("環境変数'DYNAMODB_TABLE_NAME'が設定されていません。")

# S3にアップロードする関数
def upload_to_s3(file, bucket_name, object_name):
    # S3クライアントの作成
    s3_client = boto3.client('s3')
    try:
        # ファイルのアップロード
        s3_client.upload_fileobj(file, bucket_name, object_name)
        return True
    except NoCredentialsError:
        st.error("AWSの認証情報が見つかりません。")
        return False
    except Exception as e:
        st.error(f"アップロード中にエラーが発生しました: {e}")
        return False

# アップロードボタン
if st.button('アップロード') and uploaded_file is not None:
    # ファイル名を取得（S3上のオブジェクト名として使用）
    file_name = uploaded_file.name

    # S3にアップロードする関数を呼び出し
    if upload_to_s3(uploaded_file, bucket_name, file_name):
        st.success("ファイルが正常にアップロードされました。")
    else:
        st.error("アップロードに失敗しました。")

# アップロードしたファイル名（拡張子を除く）をグローバル変数に保持
if uploaded_file is not None:
    file_name_without_extension = os.path.splitext(uploaded_file.name)[0]
else:
    file_name_without_extension = None

# DynamoDBをクエリするボタンとその処理
if st.button('DynamoDBをクエリ') and file_name_without_extension:
    record = query_dynamodb(file_name_without_extension)
    
    # クエリ結果の表示
    if record:
        st.write("DynamoDBのクエリ結果:")
        st.json(record)
    else:
        st.error("指定されたIDのレコードが見つかりませんでした。")
