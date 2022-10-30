import os
import json
import boto3
from aws_xray_sdk.core import xray_recorder
from aws_lambda_powertools import Logger, Tracer
from pythonjsonlogger import jsonlogger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths


cold_start = True
metric_namespace = 'MyApp'

logger = Logger(service="APP")
tracer = Tracer(service="APP")
metrics = boto3.client('cloudwatch')
app = APIGatewayRestResolver()

@tracer.capture_method
def add_greeting_metric(service: str = 'APP'):
    function_name = os.getenv('AWS_LAMBDA_FUNCTION_NAME', 'undefined')
    service_dimension = {
        'Name': 'Service',
        'Value': service
    }
    function_dimension = {
        'Name': 'function_name',
        'Value': function_name
    }
    is_cold_start = True
    return metrics.put_metric_data(
        MetricData = [
            {
                'MetricName': 'SuccessfullGreeting',
                'Dimensions': [ service_dimension ],
                'Unit': 'Count',
                'Value': 1
            },
            {
                'MetricName': 'ColdStart',
                'Dimensions': [ service_dimension, function_dimension ],
                'Unit': 'Count',
                'Value': int(is_cold_start)
            }
        ],
        Namespace=metric_namespace)

@app.get('/hello/<name>')
@tracer.capture_method
def hello_name(name):
    tracer.put_annotation(key='User', value=name)
    logger.info(f'Request from {name} received.')
    add_greeting_metric()
    return {
        'message': f'Hello {name} !'
    }

@app.get('/hello')
@tracer.capture_method
def hello():
    tracer.put_annotation(key='User', value='unknown')
    logger.info('Request from Unknown received.')
    add_greeting_metric()
    return {
        'message': 'hello unknown !'
    }

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    #return {
    #    "statusCode": 200,
    #    "body": json.dumps({
    #        "message": "hello world",
    #        # "location": ip.text.replace("\n", "")
    #    }),
    #}
    return app.resolve(event, context)
