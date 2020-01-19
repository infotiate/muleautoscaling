import json
import requests
import json
import boto3
import base64
from botocore.exceptions import ClientError
from json import JSONDecodeError
import http.client
import io
import logging


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def lambda_deployMuleAps(event, context):
    # TODO implement
    
    targetInfo = lambda_getTargetId(event, context)
    LOGGER.debug(targetInfo)
    
    apiMap = {
        'applications' : [
                {
                    'name' : 'HelloWorld',
                    'fileName' : 'hello-world-2.1.4-mule-application-example.jar'
                }
            ]
    }
    
    print ('Deploying... ', apiMap)
    applications = apiMap['applications']
    s3 = boto3.client('s3')
    
    for application in applications :
        LOGGER.info('*******************************************************')
        f = io.BytesIO()
        LOGGER.info('Downloading file %s', application['fileName'])
        s3.download_fileobj(event['s3Bucketname'], application['fileName'], f)
        LOGGER.info('Uploading file to runtime manager...')
        armResp = deployAppFromFile(event, application['fileName'], targetInfo['targetId'], f)
        LOGGER.info('Deployment response %s.....\n',armResp)
        LOGGER.info('*******************************************************')

#Deploy application from mule application file    
def deployAppFromFile(event, appName, targetId, applicationFile):
    armrq_headers = {
        'x-anypnt-env-id': event['envId'], 
        'x-anypnt-org-id': event['orgId'],
        'Authorization': 'Bearer ' + event.get('accessToken',""),
    }
    domain = event['domain']
    conn = http.client.HTTPSConnection(domain)
    
    armReqUrl = "/hybrid/api/v1/applications"
    
    body = {
        "artifactName": appName, 
        "targetId": targetId,
    }

    multiPartFormData = {
        'file' : (appName, applicationFile)
    }    
    
    response = requests.post('https://'+domain + armReqUrl, 
        data=body, 
        files=multiPartFormData, 
        headers=armrq_headers)
    
    return response

def lambda_getTargetId(event, context):
    # TODO implement
  # Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/

    LOGGER.info (event)

    domain = event['domain']
    conn = http.client.HTTPSConnection(domain)
    accessToken = event.get('accessToken',"")
    serverName = event.get('serverName')
    serverType = event.get('serverType', "")
    
    #Call Runtime Manager API with access token to obtain list of servers
    
    armrq_headers = {
        'x-anypnt-env-id': event['envId'], 
        'x-anypnt-org-id': event['orgId'],
        'Authorization': 'Bearer ' + accessToken
    }
    
    armReqUrl = '/hybrid/api/v1/servers'
    
    if ( serverType == 'SERVER_GROUP') :
        armReqUrl = '/hybrid/api/v1/serverGroups'
    
    LOGGER.info(armReqUrl)
    
    conn.request('GET', armReqUrl, "", armrq_headers)
    apiResponse = conn.getresponse().read().decode()
    
    arm_response = json.loads(apiResponse)['data']
    LOGGER.info(arm_response)

    for server in arm_response:
        if (server['name'] == serverName) :

            return {
                'statusCode': 200,
                'targetId': server['id'],
                'type' : server['type'],
                'status' : server['status']
            }

def lambda_addServerToGroup(event, context):
    domain = event['domain']
    conn = http.client.HTTPSConnection(domain)
    accessToken = event.get('accessToken',"")
    serverName = event.get('serverName')
    serverGroupName = event.get('serverGroupName')
    envId = event.get('envId')
    orgId = event.get('orgId')

    grpInfoReq = {
          "domain": domain,
          "envId": envId,
          "orgId": orgId,
          "accessToken": accessToken,
          "serverName": serverGroupName,
          "serverType": "SERVER_GROUP"
    }
    
    groupInfo = lambda_getTargetId(grpInfoReq, "")
    LOGGER.info("******************")
    LOGGER.info(groupInfo)
    LOGGER.info("******************")
    serverGroupId = groupInfo['targetId']
 
    srvInfoReq = {
          "domain": domain,
          "envId": envId,
          "orgId": orgId,
          "accessToken": accessToken,
          "serverName": serverName,
          "serverType": "SERVER"
    }
    serverInfo = lambda_getTargetId(srvInfoReq, "")
    LOGGER.info(serverInfo)
    serverId = serverInfo['targetId']
    LOGGER.info("******************")
    
    url = "https://anypoint.mulesoft.com/hybrid/api/v1/serverGroups/" + str(serverGroupId) + "/servers/" + str(serverId)
    headers = geArmHeaders(event)

    print(url)
    req = requests.post(url, headers=headers)

    LOGGER.info(req.status_code)
    LOGGER.info(req.headers)
    LOGGER.info(req.text)
    
    return {
        'statusCode' : 200,
        'message' : 'server added to the group'
    }
    
def geArmHeaders(event):
    headers = {
        'x-anypnt-env-id': event['envId'],
        'x-anypnt-org-id': event['orgId'],
        'Authorization': 'Bearer ' + event['accessToken']
    }
    return headers
