from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_s3_notifications as s3n,
    aws_lambda_python_alpha as lambda_python,
)
from constructs import Construct

class CertTeacherClaude3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        base_name = "y3-shimizu-cert-teacher"
        
        # S3バケットの作成
        bucket = s3.Bucket(self, base_name)

        # Lambda関数の作成
        lambda_function = lambda_python.PythonFunction(
            self, f"{base_name}-function",
            entry="lambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
        )

        # S3バケットへのPUT操作をLambda関数のトリガーとして設定
        notification = s3n.LambdaDestination(lambda_function)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, notification)
