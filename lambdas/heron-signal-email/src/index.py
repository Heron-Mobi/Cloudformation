import boto3
import os
import json


def lambda_handler(event, context):
    payload = json.loads(event["Records"][0]["body"])
    date = payload["date"]
    identityid = payload["identityID"]
    ssm = boto3.client("ssm")
    video_domain_param = ssm.get_parameter(
        Name="/heron/heron-video-domain", WithDecryption=False
    )
    video_domain = video_domain_param["Parameter"]["Value"]

    print(payload)
