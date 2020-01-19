import json
import boto3
import mulefunctions

def lambda_handler(event, context):
    # TODO implement
    detailType = event['detail-type']
    region = event['region']
    print(detailType)
    if ("EC2 Instance Terminate" not in detailType):
        print("Nothing to do!")
        return

    instance_id = event['detail']['EC2InstanceId']
    print('Removing EC2 instance iD....')
    print(instance_id)
    
    payload={"region": 'us-east-1', "tokenType": 'access'}
    
    response = mulefunctions.lambda_getArmAccessToken(payload)
    print(response)
    
    access_token = response['access_token']
    envId = response['envId']
    orgId = response['orgId']
    
    
    payload = {
          "domain": "anypoint.mulesoft.com",
          "envId": envId,
          "orgId": orgId,
          "accessToken": access_token,
          "serverName": instance_id,
          "serverGroupName": "MuleRuntimesDev",
          "action": "remove"
    }

    rmSrvResponse = mulefunctions.lambda_serverGroupAction(payload, "")
    print(rmSrvResponse)
