import json
import boto3
import botocore
import usersession.usersession as usersession


def handler(event, context):
    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "multiValueHeaders": {},
        "body": "",
    }
    identityId, session = usersession.get_user_id_and_session(
            event["headers"]["Authorization"],
            event["requestContext"]["accountId"]
            )
    cloudformation = boto3.client("cloudformation")

    try:
        stack = 'external-sqs-' + identityId['IdentityId'].replace(':', '-')
        stacks = cloudformation.describe_stacks(
            StackName=stack
        )
        status = stacks['Stacks'][0]['StackStatus']
        if status == 'CREATE_IN_PROGRESS' or status == 'DELETE_IN_PROGRESS':
            response["body"] = json.dumps({
                "sqsdeployed": False,
                "inprogress": True,
                "error": ""
            })
        else:
            response["body"] = json.dumps({
                    "sqsdeployed": True,
                    "inprogress": False,
                    "error": ""
            })

    except botocore.exceptions.ClientError as e:
        print(e.response["Error"]["Code"])
        if e.response["Error"]["Code"] == "ValidationError":
            response["body"] = json.dumps({
                "sqsdeployed": False,
                "inprogress": False
            })
        else:
            response["body"] = json.dumps({
                "sqsdeployed": False,
                "inprogress": False,
                "error": e.response["Error"]["Code"]
            })
            raise
    return response
