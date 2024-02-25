import json
import boto3
import tweepy
import botocore


def gettokens(domain, url):
    secretsmanager = boto3.client("secretsmanager")
    twittersecretvalue = secretsmanager.get_secret_value(
        SecretId="heron/integrations/twitter"
    )
    twittersecret = json.loads(twittersecretvalue["SecretString"])
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        redirect_uri="https://" + domain + "/integrations/twittertoken",
        client_id=twittersecret["clientid"],
        client_secret=twittersecret["clientsecret"],
        scope=["tweet.write", "offline.access", "tweet.read", "users.read"]
    )
    return oauth2_user_handler.fetch_token(
        url
    )


def handler(event, context):
    print(event)
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
    dashboard_domain_param = ssm.get_parameter(
        Name="/heron/heron-dashboard-domain", WithDecryption=False
    )

    domian = dashboard_domain_param["Parameter"]["Value"]

    print(gettokens(domain, event['body']))

    return response
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
    api_domain_param = ssm.get_parameter(
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
                identityId, dashboard_domain_param["Parameter"]["Value"]
            )
        else:
            raise
    return response
