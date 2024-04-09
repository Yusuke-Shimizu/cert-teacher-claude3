# app.py
import streamlit as st
import requests

# ファイルアップロードウィジェットの作成
uploaded_file = st.file_uploader("ファイルを選択してください", type=['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# アップロードボタン
if st.button('アップロード') and uploaded_file is not None:
    files = {'file': uploaded_file.getvalue()}
    response = requests.post('https://your-lambda-function-url', files=files)
    if response.status_code == 200:
        st.success("ファイルが正常にアップロードされました")
    else:
        st.error("アップロード中にエラーが発生しました")
