from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_lambda as _lambda,
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
        
        table = self.create_dynamodb_table(base_name)
        lambda_function = self.create_lambda_function(base_name, table)
        bucket = self.create_s3_bucket(base_name, lambda_function)
        self.add_outputs(bucket, table)

    def create_dynamodb_table(self, base_name: str) -> dynamodb.Table:
        return dynamodb.Table(
            self, f"{base_name}-DynamoDBTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

    def create_lambda_function(self, base_name: str, table: dynamodb.Table) -> lambda_python.PythonFunction:
        lambda_role = iam.Role(self, f"{base_name}-LambdaExecutionRole",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                               ])

        bedrock_policy_statement = iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"],
            effect=iam.Effect.ALLOW
        )

        dynamodb_policy_statement = iam.PolicyStatement(
            actions=["dynamodb:*Item"],
            resources=[table.table_arn],
            effect=iam.Effect.ALLOW
        )

        lambda_role.add_to_policy(bedrock_policy_statement)
        lambda_role.add_to_policy(dynamodb_policy_statement)

        duration_15_min = Duration.seconds(900)
        lambda_function = lambda_python.PythonFunction(
            self, f"{base_name}-function",
            entry="lambda/create_answer",
            runtime=_lambda.Runtime.PYTHON_3_12,
            role=lambda_role,
            timeout=duration_15_min,
        )
        lambda_function.add_environment(key="DYNAMODB_TABLE_NAME", value=table.table_name)
        return lambda_function

    def create_s3_bucket(self, base_name: str, lambda_function: lambda_python.PythonFunction) -> s3.Bucket:
        bucket = s3.Bucket(self, base_name)
        notification = s3n.LambdaDestination(lambda_function)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, notification)
        bucket.grant_read(lambda_function)
        return bucket

    def add_outputs(self, bucket: s3.Bucket, table: dynamodb.Table):
        CfnOutput(self, "BucketNameOutput",
                  value=bucket.bucket_name,
                  description="The name of the S3 bucket")
        CfnOutput(self, "DynamoDBTableNameOutput",
                  value=table.table_name,
                  description="The name of the DynamoDB table")
