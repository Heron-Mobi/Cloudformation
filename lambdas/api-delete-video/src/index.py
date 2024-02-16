import json
import boto3
import os


def handler(event, context):
    status = {"status": "deleted"}
    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "multiValueHeaders": {},
    }

    try:
        if (
            (event["queryStringParameters"])
            and (event["queryStringParameters"]["id"])
            and (event["queryStringParameters"]["id"] is not None)
        ):
            dateid = event["queryStringParameters"]["id"]
    except KeyError:
        print("empty date, doing nothing")
        status["status"] = "failed"
        response["body"] = json.dumps(status)
        return response

    ssm = boto3.client("ssm")
    identity_pool_param = ssm.get_parameter(
        Name="/heron/identity-pool-id", WithDecryption=False
    )
    user_pool_param = ssm.get_parameter(
        Name="/heron/user-pool-id", WithDecryption=False
    )
    video_bucket_param = ssm.get_parameter(
        Name="/heron/video-bucket-name", WithDecryption=False
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
    bucket = s3.Bucket(video_bucket_param["Parameter"]["Value"])
    try:
        bucket.objects.filter(Prefix=identityId["IdentityId"] + "/" + dateid).delete()
    except:
        status["status"] = "failed"
    response["body"] = json.dumps(status)
    return response
