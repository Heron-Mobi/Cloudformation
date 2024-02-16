import json
import boto3
import os
from datetime import datetime
def folders(client, bucket, prefix=''):
paginator = client.get_paginator('list_objects')
for result in paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter='/'):
  for prefix in result.get('CommonPrefixes', []):
    yield prefix.get('Prefix')

def handler(event, context):
print(json.dumps(event))
ssm = boto3.client('ssm')
identity_pool_param = ssm.get_parameter(
  Name = '/heron/identity-pool-id',
  WithDecryption = False
)
user_pool_param = ssm.get_parameter(
  Name = '/heron/user-pool-id',
  WithDecryption = False
)
video_bucket_param = ssm.get_parameter(
  Name = '/heron/video-bucket-name',
  WithDecryption = False
)
region = os.environ['AWS_REGION']
logins = {
  'cognito-idp.eu-central-1.amazonaws.com/' + user_pool_param['Parameter']['Value']: event['headers']['Authorization']
}
client = boto3.client('cognito-identity')
identityId = client.get_id(
  AccountId = event['requestContext']['accountId'],
  IdentityPoolId = identity_pool_param['Parameter']['Value'],
  Logins = logins
)
print(identityId)
creds = client.get_credentials_for_identity(
  IdentityId = identityId['IdentityId'],
  Logins = logins
)
userclient = boto3.client(
  's3',
  aws_access_key_id = creds['Credentials']['AccessKeyId'],
  aws_secret_access_key = creds['Credentials']['SecretKey'],
  aws_session_token = creds['Credentials']['SessionToken']
)
gen_subfolders = folders(
  userclient,
  video_bucket_param['Parameter']['Value'],
  prefix=identityId['IdentityId'] + '/'
)
videofolders = []
for folder in gen_subfolders:
  f = folder.split("/")
  out = datetime.strptime(f[1], '%d%m%Y%H%M%S')
  videofolders.append(
    {
      'id': f[1],
      'date': out.isoformat()
    }
  )

response = {
  'isBase64Encoded': False,
  'statusCode': 200,
  'headers': {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
  },
  'multiValueHeaders': {},
  'body': json.dumps({
    'videos': videofolders,
    'id': identityId,
  })
}
return response   
