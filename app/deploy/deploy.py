# from aws_cdk import (
#     aws_lambda as _lambda,
#     aws_apigateway as apigw,
#     core,
# )
from constructs import Construct
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigw
import aws_cdk as core

from zipfile import ZipFile
import os

class MyStack(core.Stack):
    
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # delete if zip file exists
        file_dir = os.path.dirname(os.path.realpath(__file__))
        zip_file_name = os.path.join(file_dir, 'lambda.zip')
        try:
            print("removing old zip file...")
            os.remove(zip_file_name)
        except OSError:
            print("No file to remove")
            pass

        # create zip file
        print("zipping file...")
        zf = ZipFile(zip_file_name, 'w')
        os.chdir(file_dir)
        os.chdir("..")
        # hopefully we can use a *.py here
        zf.write('answered.py')
        zf.write('common.py')
        zf.write('constants.py')
        zf.write('delete_prayer.py')
        zf.write('list_prayer.py')
        zf.write('main.py')
        zf.write('pray.py')
        zf.write('request_prayer.py')
        zf.close()

        # create the lambda function
        print("creating lambda...")
        handler = _lambda.Function(
            self, 'MyLambdaHandler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset(zip_file_name),
            handler='main.lambda_handler',
        )
        
        # create the API Gateway REST API
        print("creating api gw...")
        api = apigw.RestApi(
            self, 'MyRestApi',
            rest_api_name='My API Gateway',
            description='This is my API Gateway',
        )
        
        # create a resource for the API Gateway
        print("creating api gw add_resource...")
        resource = api.root.add_resource('myresource')
        
        # create a method for the API Gateway resource
        print("creating api gw add_method...")
        method = resource.add_method(
            'GET',
            apigw.LambdaIntegration(handler),
        )

app = core.App()
MyStack(app, 'MyStack')
app.synth()