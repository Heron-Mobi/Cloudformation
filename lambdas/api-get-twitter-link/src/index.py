import json
import boto3
import tweepy
import botocore
import usersession.usersession as usersession
from tweepyoverrides.tweepyoverrides import TweepyVerifierOAuth2UserHandler


def getlinkandverifier(domain):
    secretsmanager = boto3.client("secretsmanager")
    twittersecretvalue = secretsmanager.get_secret_value(
        SecretId="heron/integrations/twitter"
    )
    print(domain)
    twittersecret = json.loads(twittersecretvalue["SecretString"])
    redirect_uri = "https://" + domain + "/integrations/twittertoken"
    print(redirect_uri)
    oauth2_user_handler = TweepyVerifierOAuth2UserHandler(
        client_id=twittersecret["clientid"],
        redirect_uri=redirect_uri,
        scope=["tweet.write", "offline.access", "tweet.read", "users.read"],
        client_secret=twittersecret["clientsecret"],
    )
    return oauth2_user_handler.get_authorization_url(), oauth2_user_handler.code_verifier


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
    dash_domain_param = ssm.get_parameter(
        Name="/heron/heron-dashboard-domain", WithDecryption=False
    )
    identityId, session = usersession.get_user_id_and_session(
            event["headers"]["Authorization"],
            event["requestContext"]["accountId"]
            )
    s3 = session.resource("s3")
    link, verifier = getlinkandverifier(
            dash_domain_param["Parameter"]["Value"]
            )
    link_data = {
            'link': link,
            'set': False,
    }
    try:
        configObject = s3.Object(
            config_bucket_param["Parameter"]["Value"],
            identityId["IdentityId"] + "/twittertoken",
        )
        configObject.get()
        link_data["set"] = True
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            link_data["set"] = False
        else:
            raise
    configObject = s3.Object(
        config_bucket_param["Parameter"]["Value"],
        identityId["IdentityId"] + "/twitterverifier",
    )
    configObject.put(Body = verifier.encode('utf-8'))
    response["body"] = json.dumps(link_data)
    return response
