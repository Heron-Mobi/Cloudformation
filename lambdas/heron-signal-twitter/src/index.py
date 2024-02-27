import boto3
import json
from string import Template
from tweepyoverrides.tweepyoverrides import TweepyRefreshAuth2UserHandler
import tweepy


def lambda_handler(event, context):
    payload = json.loads(event["Records"][0]["body"])
    date = payload["date"]
    identityid = payload["identityID"]
    twitter_handle = payload["config"]["twitter-handle"]




    ssm = boto3.client("ssm")
    s3 = boto3.client("s3")
    secretsmanager = boto3.client("secretsmanager")

    video_domain_param = ssm.get_parameter(
        Name="/heron/heron-video-domain", WithDecryption=False
    )
    video_bucket_param = ssm.get_parameter(
        Name="/heron/video-bucket-name", WithDecryption=False
    )
    config_bucket_param = ssm.get_parameter(
        Name="/heron/config-bucket-name", WithDecryption=False
    )
    video_bucket = video_bucket_param["Parameter"]["Value"]
    config_bucket = config_bucket_param["Parameter"]["Value"]
    video_domain = video_domain_param["Parameter"]["Value"]
    twittersecretvalue = secretsmanager.get_secret_value(
        SecretId="heron/integrations/twitter"
    )
    twittersecret = json.loads(twittersecretvalue["SecretString"])
    dash_domain_param = ssm.get_parameter(
        Name="/heron/heron-dashboard-domain", WithDecryption=False
    )
    dash_domain = dash_domain_param["Parameter"]["Value"]
    tokenObject = s3.Object(
        config_bucket,
        identityid + "/twittertoken",
    )
    tokens = json.loads(tokenObject.get()['Body'].read())
    



    camtemplate = ""
    with open('template.html', 'r') as file:
        camtemplate = Template(file.read())
   
    camstring = camtemplate.substitute(
        date=date,
        identityid=identityid,
        twitter_handle=twitter_handle,
        video_domain=video_domain,
    )
    s3 = boto3.resource("s3")
    camobject = s3.Object(
        bucket_name=video_bucket,
        key=identityid + "/" + date + "/twitter.html"
    )
    camobject.put(Body=camstring, ContentType="text/html")


    auth = TweepyRefreshAuth2UserHandler(
        redirect_uri="https://" + dash_domain + "/integrations/twittertoken",
        client_id=twittersecret["clientid"],
        client_secret=twittersecret["clientsecret"],
        scope=["tweet.write", "offline.access", "tweet.read", "users.read"],
    )
    newtokens = auth.refresh_token(tokens['refresh_token'])

    tokenObject.put(Body=json.dumps(newtokens).encode())
    client = tweepy.Client(bearer_token=tokens['access_token'])
    resp = client.create_tweet(text="heron test heron test", user_auth=False)
    print(resp)
