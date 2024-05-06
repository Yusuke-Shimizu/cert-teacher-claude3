import invoke
import logging
import os
import boto3

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
    invoke.run("pip install -r requirements.txt -r requirements-dev.txt")

@invoke.task
def install_direnv(c):
    logging.info("install_direnv")
    # ファイルパスを指定
    file_path = '/usr/local/bin/direnv'
    
    # ファイルが存在するかどうかを確認
    if not os.path.exists(file_path):
        logging.info(f"{file_path} ファイルが存在しないのでインストールを開始します。")
        bashrc_path = "~/.bashrc"
        direnv_version="2.33.0" # Check https://github.com/direnv/direnv/releases

        # Install
        logging.info("Install direnv")
        invoke.run(f"wget -O direnv https://github.com/direnv/direnv/releases/download/v{direnv_version}/direnv.linux-amd64")
        invoke.run("chmod +x direnv")
        invoke.run("sudo mv direnv /usr/local/bin/")
        
        # Set bashrc
        logging.info("Set bashrc")
        invoke.run("echo 'eval \"$(direnv hook bash)\"' >> ~/.bashrc")
        logging.info(f"Exec below command")
        logging.info(f"source {bashrc_path}")
        logging.info(f"direnv --help")

    logging.info("Finish install_direnv")


@invoke.task
def diff(c):
    invoke.run("cdk diff", pty=True,)

@invoke.task
def deploy(c):
    logging.info("deploy")
    invoke.run("cdk deploy --require-approval never", pty=True,)
    logging.info("finish")

@invoke.task
def hotswap(c):
    logging.info("hotswap deploy")
    invoke.run("cdk deploy --require-approval never --hotswap", pty=True,)
    logging.info("finish")

@invoke.task
def front(c):
    logging.info("start frontend")
    invoke.run("streamlit run frontend/app.py --logger.level=debug", pty=True,)
    logging.info("finish")
