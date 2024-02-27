import json
import boto3
from datetime import datetime
import usersession.usersession as usersession


def folders(client, bucket, prefix=""):
    paginator = client.get_paginator("list_objects")
    for result in paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter="/"):
        for prefix in result.get("CommonPrefixes", []):
            yield prefix.get("Prefix")


def handler(event, context):
    print(json.dumps(event))
    ssm = boto3.client("ssm")
    video_bucket_param = ssm.get_parameter(
        Name="/heron/video-bucket-name", WithDecryption=False
    )
    identityId, session = usersession.get_user_id_and_session(
            event["headers"]["Authorization"],
            event["requestContext"]["accountId"]
            )
    s3 = session.client("s3")
    gen_subfolders = folders(
        s3,
        video_bucket_param["Parameter"]["Value"],
        prefix=identityId["IdentityId"] + "/",
    )
    videofolders = []
    for folder in gen_subfolders:
        f = folder.split("/")
        out = datetime.strptime(f[1], "%d%m%Y%H%M%S")
        videofolders.append({"id": f[1], "date": out.isoformat()})

    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "multiValueHeaders": {},
        "body": json.dumps(
            {
                "videos": videofolders,
                "id": identityId,
            }
        ),
    }
    return response
