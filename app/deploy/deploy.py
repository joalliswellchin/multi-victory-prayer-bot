# from aws_cdk import (
#     aws_lambda as _lambda,
#     aws_apigateway as apigw,
#     core,
# )
from constructs import Construct
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigw
import aws_cdk as core

class MyStack(core.Stack):
    
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # create the lambda function
        handler = _lambda.Function(
            self, 'MyLambdaHandler',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambda'),
            handler='handler.handle',
        )
        
        # create the API Gateway REST API
        api = apigw.RestApi(
            self, 'MyRestApi',
            rest_api_name='My API Gateway',
            description='This is my API Gateway',
        )
        
        # create a resource for the API Gateway
        resource = api.root.add_resource('myresource')
        
        # create a method for the API Gateway resource
        method = resource.add_method(
            'GET',
            apigw.LambdaIntegration(handler),
        )

app = core.App()
MyStack(app, 'MyStack')
app.synth()