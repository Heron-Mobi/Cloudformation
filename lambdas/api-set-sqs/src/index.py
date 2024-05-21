import json
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
    sqs = session.client("sqs")
    queues = sqs.list_queues(QueueNamePrefix='external-sqs-' + identityId)

    response["body"] = json.dumps(queues['QueueUrls'][0])
    return response
