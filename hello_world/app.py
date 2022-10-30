
import json
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit

logger = Logger(service="APP")
tracer = Tracer(service="APP")
metrics = Metrics(namespace='MyApp', service='APP')
app = APIGatewayRestResolver()

@app.get('/hello/<name>')
@tracer.capture_method
def hello_name(name):
    tracer.put_annotation(key='User', value=name)
    logger.info(f'Request from {name} received.')
    metrics.add_metric(name='SuccessfulGreetings', unit=MetricUnit.Count, value=1)
    return {
        'message': f'Hello {name} !'
    }

@app.get('/hello')
@tracer.capture_method
def hello():
    tracer.put_annotation(key='User', value='unknown')
    logger.info('Request from Unknown received.')
    metrics.add_metric(name='SuccessfulGreetings', unit=MetricUnit.Count, value=1)
    return {
        'message': 'hello unknown !'
    }

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
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
    try:
        return app.resolve(event, context)
    except Exception as e:
        logger.exception(e)
        raise
