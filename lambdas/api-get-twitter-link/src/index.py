import json
import boto3
import tweepy
import botocore


def getlink(domain):
    secretsmanager = boto3.client("secretsmanager")
    twittersecretvalue = secretsmanager.get_secret_value(
        SecretId="heron/integrations/twitter"
    )
    print(domain)
    twittersecret = json.loads(twittersecretvalue["SecretString"])
    redirect_uri="https://" + domain + "/integrations/twittertoken"
    print(redirect_uri)
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=twittersecret["clientid"],
        redirect_uri = redirect_uri,
        scope=["tweet.write", "offline.access", "tweet.read", "users.read"],
        client_secret=twittersecret["clientsecret"],
    )
    return oauth2_user_handler.get_authorization_url()


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
    dash_domain_param = ssm.get_parameter(
        Name="/heron/heron-dashboard-domain", WithDecryption=False
    )
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
        configObject = s3.Object(
            config_bucket_param["Parameter"]["Value"],
            identityId["IdentityId"] + "/twittertoken",
        )
        configObject.get()
        response["body"] = "done"
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AccessDenied":
            response["body"] = getlink(
                dash_domain_param["Parameter"]["Value"]
            )
        else:
            raise
    return response
