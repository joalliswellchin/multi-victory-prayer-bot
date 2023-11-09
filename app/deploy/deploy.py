# THIS FILE USES CDK TO GENERATE AND DEPLOY CLOUDFORMATION
from constructs import Construct
from aws_cdk import aws_s3 as _s3
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigw
from aws_cdk import App, Stack
from aws_cdk.aws_iam import Effect, PolicyStatement

import boto3
import botocore

from zipfile import ZipFile
import os
import json
from dotenv import load_dotenv


class MVPBotStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # delete if zip file exists
        file_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = "lambda.zip"
        zip_file_name = os.path.join(file_dir, file_name)
        try:
            print("removing old zip file...")
            os.remove(zip_file_name)
        except OSError:
            print("No file to remove")
            pass

        # create zip file
        print("zipping file...")
        zf = ZipFile(zip_file_name, "w")
        os.chdir(file_dir)
        os.chdir("..")
        # hopefully we can use a *.py here
        zf.write("answered.py")
        zf.write("common.py")
        zf.write("constants.py")
        zf.write("delete_prayer.py")
        zf.write("list_prayer.py")
        zf.write("main.py")
        zf.write("pray.py")
        zf.write("request_prayer.py")
        zf.close()

        # create the lambda function
        print("creating lambda...")
        handler = _lambda.Function(
            self,
            "MyLambdaHandler",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset(zip_file_name),
            handler="main.lambda_handler",
        )

        # create the API Gateway REST API
        print("creating api gw...")
        api = apigw.RestApi(
            self,
            "MyRestApi",
            rest_api_name="My API Gateway",
            description="This is my API Gateway",
        )

        # create a resource for the API Gateway
        print("creating api gw add_resource...")
        resource = api.root.add_resource("myresource")

        # create a method for the API Gateway resource
        print("creating api gw add_method...")
        method = resource.add_method(
            "GET",
            apigw.LambdaIntegration(handler),
        )


# Steps to create a cloudformation json
print("Initializing App... ")
app = App()
print("App ready")
print("Creating MVPBotStack... ")
stack_name = "MVPBotStack"
stack = MVPBotStack(app, stack_name)
print("MVPBotStack ready")
print("Creating Cloud Assembly for CloudFormation... ")
cloud_assembly = app.synth()
template = cloud_assembly.get_stack_by_name(stack.stack_name).template
print("CloudFormation ready")

# Write CloudFormation template to file
print("Writing mvp_bot_cloudformation... ")
with open(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "mvp_bot_cloudformation.json"
    ),
    "w",
) as f:
    f.write(json.dumps(template, indent=4))
print("mvp_bot_cloudformation created")

# Read the CloudFormation template and send to AWS
# Get credentials
print("Getting botocore info... ")
bc_session = botocore.session.get_session()
access_key = bc_session.get_credentials().access_key
secret_key = bc_session.get_credentials().secret_key
region = bc_session.get_config_variable("region")
# Create a boto3 session with credentials
print("Creating boto3 session... ")
session = boto3.Session(
    aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region
)


# Create s3

# Add SSM
ssm = boto3.client("ssm")
load_dotenv(os.getcwd() + "/.env")
print(os.getcwd() + "/.env")
ssm_id = os.environ.get("SSM_ID")
print(f"/cdk-bootstrap/{ssm_id}/version")
ssm.put_parameter(
    Name=f"/cdk-bootstrap/{ssm_id}/version", Value="6", Type="String", Overwrite=True
)

# Use the session to create a client for the desired AWS service
print("Creating CloudFormation... ")
cloudformation_client = session.client("cloudformation")
cloudformation_client.create_stack(
    StackName=stack_name,
    TemplateBody=json.dumps(template),
    Capabilities=["CAPABILITY_NAMED_IAM"],
)
