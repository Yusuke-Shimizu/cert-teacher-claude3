from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_s3_notifications as s3n,
    aws_lambda_python_alpha as lambda_python,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

class CertTeacherClaude3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        base_name = "y3-shimizu-cert-teacher"
        
        # S3バケットの作成
        bucket = s3.Bucket(self, base_name)

        # DynamoDBテーブルの作成
        table = dynamodb.Table(
            self, f"{base_name}-DynamoDBTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create an IAM role for the Lambda function
        lambda_role = iam.Role(self, f"{base_name}-LambdaExecutionRole",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                                   # Include any other managed policies your function needs
                               ])

        # Define the policy for invoking Claude-3 model on AWS Bedrock
        bedrock_policy_statement = iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"],
            effect=iam.Effect.ALLOW
        )

        # Define the policy for accessing the DynamoDB table
        dynamodb_policy_statement = iam.PolicyStatement(
            actions=["dynamodb:*Item"],
            resources=[table.table_arn],
            effect=iam.Effect.ALLOW
        )

        # Attach the policy statement to the Lambda role
        lambda_role.add_to_policy(bedrock_policy_statement)
        lambda_role.add_to_policy(dynamodb_policy_statement)

        # Lambda関数の作成
        duration_15_min = Duration.seconds(900)
        lambda_function = lambda_python.PythonFunction(
            self, f"{base_name}-function",
            entry="lambda/create_answer",
            runtime=lambda_.Runtime.PYTHON_3_12,
            role=lambda_role,
            timeout=duration_15_min,
        )

        # S3バケットへのPUT操作をLambda関数のトリガーとして設定
        notification = s3n.LambdaDestination(lambda_function)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, notification)

        # Grant the Lambda function permissions to read objects in the S3 bucket
        bucket.grant_read(lambda_function)

        # Lambda関数にDynamoDBテーブル名を環境変数として設定
        lambda_function.add_environment(key="DYNAMODB_TABLE_NAME", value=table.table_name)

        ### api ###
        
        # アウトプットの追加
        CfnOutput(self, "BucketNameOutput",
                  value=bucket.bucket_name,
                  description="The name of the S3 bucket")
        CfnOutput(self, "DynamoDBTableNameOutput",
                  value=table.table_name,
                  description="The name of the DynamoDB table")
