import os


def handler(event, context):

    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "https://" + os.environ["ORIGINDOMAIN"],
            "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,PATCH,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,AccessAuthorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Credentials": True,
        },
    }
    return response
