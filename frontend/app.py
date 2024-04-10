# app.py
import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import os

# ファイルアップロードウィジェットの作成
uploaded_file = st.file_uploader("ファイルを選択してください", type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# 環境変数からバケット名を取得
bucket_name = os.getenv('BUCKET_NAME')
if bucket_name is None:
    st.error("環境変数'BUCKET_NAME'が設定されていません。")

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
