import os
import logging
import json
from pythonjsonlogger import jsonlogger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

logger = logging.getLogger("APP")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(fmt='%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

app = APIGatewayRestResolver()

@app.get('/hello/<name>')
def hello_name(name):
    logger.info(f'Request from {name} received.')
    return {
        'message': f'Hello {name} !'
    }

@app.get('/hello')
def hello():
    logger.info('Request from Unknown received.')
    return {
        'message': 'hello unknown !'
    }

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
    logger.debug(event)
    return app.resolve(event, context)
