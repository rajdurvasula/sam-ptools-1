import json

# import requests


def hello_name(event, **kargs):
    username = event['pathParameters']['name']
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Hello {username} !'
        })
    }

def hello(**kargs):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'hello unknown !'
        })
    }

class Router:
    def __init__(self):
        self.routes = {}
    
    def set(self, path, method, handler):
        self.routes[f"{path}-{method}"] = handler
    
    def get(self, path, method):
        try:
            return self.routes[f"{path}-{method}"]
        except KeyError:
            raise RuntimeError(f'Cannot route request to correct method. path={path}, method={method}')

router = Router()
router.set(path='/hello', method='GET', handler=hello)
router.set(path='/hello/{name}', method='GET', handler=hello_name)

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
    path = event['resource']
    http_method = event['httpMethod']
    route = router.get(path=path, method=http_method)
    return route(event=event)
    
