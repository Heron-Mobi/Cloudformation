import boto3
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
    ssm = boto3.client("ssm")
    config_bucket_param = ssm.get_parameter(
        Name="/heron/config-bucket-name", WithDecryption=False
    )
    identityId, session = usersession.get_user_id_and_session(
            event["headers"]["Authorization"],
            event["requestContext"]["accountId"]
            )
    s3 = session.resource("s3")
    configobject = s3.Object(
        config_bucket_param["Parameter"]["Value"],
        identityId["IdentityId"] + "/config.json",
    )
    configobject.put(Body=event["body"])
    return response
