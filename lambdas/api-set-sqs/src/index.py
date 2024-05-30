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

    template = 'sqsstack.yaml'
    stack = 'external-sqs-' + identityId['IdentityId'].replace(':', '-')
    yamlfile = open(template, 'r', encoding="utf-8").read()
    cloudformation = boto3.client('cloudformation')

    action = event["body"].replace('"', '')
    print(action)
    if action == "create":
        try:
            cloudformation.create_stack(
                StackName=stack,
                TemplateBody=yamlfile,
                Parameters=[{
                    'ParameterKey': 'IdentityID',
                    'ParameterValue': identityId['IdentityId']
                }],
                Capabilities=[
                    'CAPABILITY_IAM',
                    'CAPABILITY_NAMED_IAM'
                ],
                OnFailure='DELETE'
            )
            response["body"] = json.dumps({
                    "sqsdeployed": True,
                    "inprogress": True,
                    "error": ""
                })

        except botocore.exceptions.ClientError as e:
            response["body"] = json.dumps({
                "sqsdeployed": False,
                "inprogress": False,
                "error": e.response["Error"]["Code"]
            })
    elif action == "delete":
        try:
            cloudformation.delete_stack(
                StackName=stack,
            )
            response["body"] = json.dumps({
                    "sqsdeployed": False,
                    "inprogress": True,
                    "error": ""
                })
        except botocore.exceptions.ClientError as e:
            response["body"] = json.dumps({
                "sqsdeployed": True,
                "inprogress": False,
                "error": e.response["Error"]["Code"]
            })

    else:
        response["body"] = json.dumps({
                "sqsdeployed": True,
                "inprogress": False,
                "error": "invalid choice",
            })
    return response
