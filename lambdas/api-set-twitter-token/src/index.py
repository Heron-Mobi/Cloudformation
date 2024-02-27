import json
import boto3
import usersession.usersession as usersession
from tweepyoverrides.tweepyoverrides import TweepyVerifierOAuth2UserHandler


def gettokens(domain, url, verifier):
    print(domain)
    print(url)
    print(verifier)

    secretsmanager = boto3.client("secretsmanager")
    twittersecretvalue = secretsmanager.get_secret_value(
        SecretId="heron/integrations/twitter"
    )
    twittersecret = json.loads(twittersecretvalue["SecretString"])
    oauth2_user_handler = TweepyVerifierOAuth2UserHandler(
        redirect_uri="https://" + domain + "/integrations/twittertoken",
        client_id=twittersecret["clientid"],
        client_secret=twittersecret["clientsecret"],
        scope=["tweet.write", "offline.access", "tweet.read", "users.read"],
        code_verifier=verifier
    )
    return oauth2_user_handler.fetch_token(
        url.replace('"', '')
    )


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
    configObject = s3.Object(
        config_bucket_param["Parameter"]["Value"],
        identityId["IdentityId"] + "/twitterverifier",
    )
    verifier = configObject.get()['Body'].read()

    tokens = gettokens(
         dash_domain_param["Parameter"]["Value"],
         event['body'],
         verifier.decode('utf-8')
        )
    print(tokens)
    configObject = s3.Object(
        config_bucket_param["Parameter"]["Value"],
        identityId["IdentityId"] + "/twittertoken",
    )
    configObject.put(Body=json.dumps(tokens).encode())
    configObject = s3.Object(
        config_bucket_param["Parameter"]["Value"],
        identityId["IdentityId"] + "/twitterverifier",
    )
    verifier = configObject.delete()
    return response
