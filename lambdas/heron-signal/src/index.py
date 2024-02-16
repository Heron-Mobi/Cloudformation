import boto3
import botocore
import os
import json


def lambda_handler(event, context):
    print(event)
    ssm = boto3.client("ssm")
    config_bucket_param = ssm.get_parameter(
        Name="/heron/config-bucket-name", WithDecryption=False
    )
    config_bucket = config_bucket_param["Parameter"]["Value"]

    payload = json.loads(event["Records"][0]["body"])
    date = payload["date"]
    identityid = payload["identityID"]
    submitteduuid = payload["uuid"]
    s3 = boto3.resource("s3")
    obj = s3.Object(config_bucket, identityid + "/uuid").get()
    uuid = obj["Body"].read().decode("utf-8")
    print(uuid)
    if submitteduuid != uuid:
        print("Illegal ID " + submitteduuid)
        return
    try:
        obj = s3.Object(config_bucket, identityid + "/config.json").get()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            print("No config file found skipping")
            return
        else:
            raise
    config = json.loads(obj["Body"].read().decode("utf-8"))
    for signal in config["signals"]:
        signaltargetsqs_param = ssm.get_parameter(
            Name="/heron/signal-lambda/" + signal["signal-type"]
        )
        sqs = boto3.client("sqs")
        message = {"config": signal["config"], "date": date, "identityID": identityid}
        sqs.send_message(
            QueueUrl=signaltargetsqs_param["Parameter"]["Value"],
            MessageBody=json.dumps(message),
        )
