from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    core,
)

class MyStack(core.Stack):
    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
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
