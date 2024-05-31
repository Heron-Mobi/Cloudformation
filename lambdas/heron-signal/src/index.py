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
    try:
        obj = s3.Object(config_bucket, identityid + "/uuid")
        objcontents = obj.get()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            print("No uuid file found skipping")
            return
        else:
            raise
    uuid = objcontents["Body"].read().decode("utf-8")
    print(uuid)
    if submitteduuid != uuid:
        print("Illegal ID " + submitteduuid)
        return
    else:
        obj.delete()
    try:
        obj = s3.Object(config_bucket, identityid + "/config.json").get()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            print("No config file found skipping")
            return
        else:
            raise
    config = json.loads(obj["Body"].read().decode("utf-8"))
    sqserrors = {}
    sqs = boto3.client("sqs")
    for signal in config["signals"]:
        signaltargetsqs_param = ssm.get_parameter(
            Name="/heron/signal-lambda/" + signal["signal-type"]
        )
        message = {"config": signal["config"], "date": date, "identityID": identityid}
        try:
            sqs.send_message(
                QueueUrl=signaltargetsqs_param["Parameter"]["Value"],
                MessageBody=json.dumps(message),
            )
        except botocore.exceptions.ClientError as e:
            print(e)
            sqserrors[signal["config"]] = e
    accountid = event["Records"][0]["eventSourceARN"].split(":")[4]
    region = os.environ["AWS_REGION"]
    usersqs = 'lambdasignal-external-sqs-' + identityid.replace(':', '-')
    usersqsurl = "https://sqs." + region + ".amazonaws.com/" + accountid + "/" + usersqs
    message = {"config": "external-sqs", "date": date, "identityID": identityid}
    try:
        sqs.send_message(
            QueueUrl=usersqsurl,
            MessageBody=json.dumps(message),
        )
    except botocore.exceptions.ClientError as e:
        print(e)
        if e.response["Error"]["Code"] != 'QueueDoesNotExist':
            sqserrors["external-sqs"] = e

    if sqserrors:
        print(sqserrors)
        raise ValueError('SQS write errors.')
