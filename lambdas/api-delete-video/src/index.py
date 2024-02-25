import json
import boto3
import os
import usersession.usersession as usersession


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
    video_bucket_param = ssm.get_parameter(
        Name="/heron/video-bucket-name", WithDecryption=False
    )
    identityId, session = usersession.get_user_id_and_session(
            event["headers"]["Authorization"],
            event["requestContext"]["accountId"]
            )
    s3 = session.resource("s3")
    bucket = s3.Bucket(video_bucket_param["Parameter"]["Value"])
    try:
        bucket.objects.filter(Prefix=identityId["IdentityId"] + "/" + dateid).delete()
    except:
        status["status"] = "failed"
    response["body"] = json.dumps(status)
    return response
