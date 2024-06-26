import invoke
import logging
import os
import boto3
import json

logger = logging.getLogger(__name__)
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)


@invoke.task
def create_venv(c):
    """Create a virtual environment."""
    c.run("python3 -m venv .venv")
    print("Virtual environment created at .venv/")
    print("source .venv/bin/activate.fish")


@invoke.task
def install(c):
    c.run("pip install -r requirements.txt -r requirements-dev.txt")


@invoke.task
def install_direnv(c):
    logging.info("install_direnv")
    # ファイルパスを指定
    file_path = "/usr/local/bin/direnv"

    # ファイルが存在するかどうかを確認
    if not os.path.exists(file_path):
        logging.info(f"{file_path} ファイルが存在しないのでインストールを開始します。")
        bashrc_path = "~/.bashrc"
        direnv_version = "2.33.0"  # Check https://github.com/direnv/direnv/releases

        # Install
        logging.info("Install direnv")
        c.run(
            f"wget -O direnv https://github.com/direnv/direnv/releases/download/v{direnv_version}/direnv.linux-amd64"
        )
        c.run("chmod +x direnv")
        c.run("sudo mv direnv /usr/local/bin/")

        # Set bashrc
        logging.info("Set bashrc")
        c.run("echo 'eval \"$(direnv hook bash)\"' >> ~/.bashrc")
        logging.info(f"Exec below command")
        logging.info(f"source {bashrc_path}")
        logging.info(f"direnv --help")

    logging.info("Finish install_direnv")


@invoke.task
def diff(c):
    c.run(
        "cdk diff",
        pty=True,
    )


@invoke.task
def deploy(c):
    logging.info("deploy")
    c.run(
        "cdk deploy --require-approval never",
        pty=True,
    )
    logging.info("finish")


@invoke.task
def destroy(c):
    logging.info("destroy")
    c.run(
        "cdk destroy",
        pty=True,
    )
    logging.info("finish")


@invoke.task
def hotswap(c):
    logging.info("hotswap deploy")
    c.run(
        "cdk deploy --require-approval never --hotswap",
        pty=True,
    )
    logging.info("finish")


@invoke.task
def front(c):
    logging.info("start frontend")
    c.run(
        "streamlit run frontend/app.py --logger.level=debug",
        pty=True,
    )
    logging.info("finish")


@invoke.task
def allow(c):
    c.run(
        "direnv allow",
        pty=True,
    )


@invoke.task
def view_dynamodb_data(c, item_id):
    logging.info("view_dynamodb_data")
    table_name = os.getenv("DYNAMODB_TABLE_NAME")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    try:
        # item_id = "dea01"
        response = table.get_item(Key={"id": item_id})
        item = response.get("Item", None)
        if item:
            logging.info("Item found:")
            logging.info(json.dumps(item, indent=4, ensure_ascii=False))
        else:
            logging.error("指定されたIDのレコードが見つかりませんでした。")
    except Exception as e:
        logging.error(f"DynamoDBからのクエリ中にエラーが発生しました: {e}")

    logging.info("finish view_dynamodb_data")
