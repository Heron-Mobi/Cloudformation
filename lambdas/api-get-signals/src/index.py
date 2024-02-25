import json
import boto3
import botocore
import os


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
    identity_pool_param = ssm.get_parameter(
        Name="/heron/identity-pool-id", WithDecryption=False
    )
    user_pool_param = ssm.get_parameter(
        Name="/heron/user-pool-id", WithDecryption=False
    )
    config_bucket_param = ssm.get_parameter(
        Name="/heron/config-bucket-name", WithDecryption=False
    )
    region = os.environ["AWS_REGION"]
    logins = {
        "cognito-idp.eu-central-1.amazonaws.com/"
        + user_pool_param["Parameter"]["Value"]: event["headers"]["Authorization"]
    }
    client = boto3.client("cognito-identity")
    identityId = client.get_id(
        AccountId=event["requestContext"]["accountId"],
        IdentityPoolId=identity_pool_param["Parameter"]["Value"],
        Logins=logins,
    )
    creds = client.get_credentials_for_identity(
        IdentityId=identityId["IdentityId"], Logins=logins
    )
    session = boto3.Session(
        aws_access_key_id=creds["Credentials"]["AccessKeyId"],
        aws_secret_access_key=creds["Credentials"]["SecretKey"],
        aws_session_token=creds["Credentials"]["SessionToken"],
    )
    s3 = session.resource("s3")
    try:
        configobject = s3.Object(
            config_bucket_param["Parameter"]["Value"],
            identityId["IdentityId"] + "/config.json",
        )
        response["body"] = configobject.get()["Body"].read().decode("utf-8")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "AccessDenied":
            response["body"] = json.dumps({'signals':[]})
        else:
            raise
    return response
