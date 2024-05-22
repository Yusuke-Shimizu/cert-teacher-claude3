import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import os

# 環境変数から必要な情報を取得
bucket_name = os.getenv("BUCKET_NAME")
table_name = os.getenv("DYNAMODB_TABLE_NAME")

# 必要な環境変数が設定されていない場合はエラーを表示して処理をここで停止
if not bucket_name or not table_name:
    missing_vars = ", ".join(
        [
            var
            for var, value in [
                ("BUCKET_NAME", bucket_name),
                ("DYNAMODB_TABLE_NAME", table_name),
            ]
            if not value
        ]
    )
    st.error(f"環境変数'{missing_vars}'が設定されていません。")
    st.stop()

# DynamoDBテーブル名の確認
# AWSリージョンを指定
dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
table = ""
try:
    # テーブルが存在するか確認
    table = dynamodb.Table(table_name)
    if table.table_status not in ["CREATING", "UPDATING", "DELETING", "ACTIVE"]:
        st.error(f"DynamoDBテーブル'{table_name}'の状態が不正です。")
        st.stop()
except dynamodb.meta.client.exceptions.ResourceNotFoundException:
    st.error(f"DynamoDBテーブル'{table_name}'が存在しません。")
    st.stop()


# AWSリソースのクライアントを作成する関数
def create_client(service_name):
    try:
        return boto3.client(service_name)
    except NoCredentialsError:
        st.error(f"AWSの認証情報が見つかりません。")
        return None


# S3にアップロードする関数
def upload_to_s3(file, bucket_name, object_name):
    s3_client = create_client("s3")
    if s3_client is None:
        return False
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        return True
    except Exception as e:
        st.error(f"アップロード中にエラーが発生しました: {e}")
        return False


# DynamoDBにクエリする関数
def query_dynamodb(file_name_without_extension):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key={"id": file_name_without_extension})
        return response.get("Item", None)
    except Exception as e:
        st.error(f"DynamoDBからのクエリ中にエラーが発生しました: {e}")
        return None


# 初期化処理
if "upload_button_clicked" not in st.session_state:
    st.session_state.upload_button_clicked = False
if "question_button_clicked" not in st.session_state:
    st.session_state.question_button_clicked = False
if "answer_button_clicked" not in st.session_state:
    st.session_state.answer_button_clicked = False

# ファイルアップロードウィジェットの作成
uploaded_file = st.file_uploader(
    "ファイルを選択してください", type=["png", "jpg", "jpeg", "gif"]
)

# アップロードボタン
if st.button("アップロード") and uploaded_file:
    st.session_state.upload_button_clicked = True

if st.session_state.upload_button_clicked:
    file_name = uploaded_file.name
    if upload_to_s3(uploaded_file, bucket_name, file_name):
        st.success("ファイルが正常にアップロードされました。")
        st.session_state["uploaded_file_name"] = (
            file_name  # セッション状態にファイル名を保存
        )

        # アップロードしたファイル名（拡張子を除く）をセッション状態に保存
        st.session_state["file_name_without_extension"] = (
            os.path.splitext(uploaded_file.name)[0] if uploaded_file else None
        )

print("uploaded_file_name")
print(st.session_state.get("uploaded_file_name", ""))
print("file_name_without_extension")
print(st.session_state.get("file_name_without_extension", ""))

# DynamoDBをクエリするボタンとその処理
# if st.button("問題を見る") and st.session_state.get("uploaded_file_name"):
if st.button("問題を見る"):
    st.session_state.question_button_clicked = True

if st.session_state.question_button_clicked:
    record = query_dynamodb(st.session_state.get("file_name_without_extension", ""))
    print("record")
    print(record)
    if record:
        st.session_state["japanese_question"] = record.get(
            "japanese_question", "日本語の問題が見つかりません"
        )
        st.write(st.session_state["japanese_question"])
    else:
        st.error("指定されたIDのレコードが見つかりませんでした。")

# 回答を見るボタン
if st.button("回答を見る"):
    st.session_state.answer_button_clicked = True

if st.session_state.answer_button_clicked:
    st.session_state["answer"] = record.get("answer", "回答が見つかりません")
    if "answer" in st.session_state and "japanese_question" in st.session_state:
        st.write(st.session_state["answer"])
    else:
        st.error("問題を先に表示してください。")
