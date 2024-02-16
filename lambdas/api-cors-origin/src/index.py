import json
import boto3


def handler(event, context):
    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,PATCH,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,AccessAuthorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Credentials": True,
        },
    }
    return response
