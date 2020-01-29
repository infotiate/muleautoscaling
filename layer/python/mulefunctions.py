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

def lambda_getArmAccessToken(event):
    return lambda_getAccessTokenFromConnecedApp(event)


def lambda_getArmAccessTokenFromUser(event):
    # TODO implement
  # Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/

    print (event)

    secret_name = "MuleAnypointUser"
    region_name =  event['region']
    tokenType = event.get('tokenType',"")
    
    secret = ""
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({ "error":"Error processing your request " + e.response["Error"]["Code"]})
        }
     
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
     
    if (len(secret) <= 0) :
        return {
            'statusCode': 400,
            'body': json.dumps('{ "error":"Bad request"}')
        }
    
    p = json.loads(secret)
    domain = p['muleDomainUrl']
    user = p['muleAnypointUser']
    envId = p['envId']
    orgId = p['orgId']
    
    conn = http.client.HTTPSConnection(domain)
    
    #Login to Mulesoft and obtain access token
    
    url = '/accounts/login' 
    headers = {'Content-Type': 'application/json'}
    body = json.dumps({'username': user, 'password':p['muleAnypointUserPassword']})
    conn.request('POST', url, body, headers)
    response = conn.getresponse()
    
    anypoint_access_token = json.loads(response.read().decode())['access_token']
    
    print("Access token",anypoint_access_token)
    
    if (tokenType == 'access') :
        #Return the registration response
        return {
            'statusCode': 200,
            'access_token': anypoint_access_token,
            'envId': envId,
            'orgId': orgId 
        }
    
    #Call Runtime Manager API with access token obtained in the previous call 
    #to obtain registration token
    
    armrq_headers = {
        'x-anypnt-env-id': envId, 
        'x-anypnt-org-id': orgId,
        'Authorization': 'Bearer ' + anypoint_access_token
    }
       
    
    armReqUrl = '/hybrid/api/v1/servers/registrationToken'
    conn.request('GET', armReqUrl, "", armrq_headers)
    arm_response = json.loads(conn.getresponse().read().decode())['data']
    
    
    #Return the registration response
    return {
        'statusCode': 200,
        'registration_token': json.dumps(arm_response),
        'access_token': anypoint_access_token,
        'envId': envId,
        'orgId': orgId 
    }


def lambda_getAccessTokenFromConnecedApp(event):
    # TODO implement
  # Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/

    print (event)

    secret_name = "MuleAnypointUser"
    region_name =  event['region']
    tokenType = event.get('tokenType',"")
    
    secret = ""
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({ "error":"Error processing your request " + e.response["Error"]["Code"]})
        }
     
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
     
    if (len(secret) <= 0) :
        return {
            'statusCode': 400,
            'body': json.dumps('{ "error":"Bad request"}')
        }
    
    p = json.loads(secret)
    domain = p['muleDomainUrl']
    envId = p['envId']
    orgId = p['orgId']
    client_id = p['client_id']
    client_secret = p['client_secret']
    
    conn = http.client.HTTPSConnection(domain)
    
    #Obtain Access token
    
    payload = {'client_id': client_id, 
                'client_secret': client_secret,
                'grant_type' : 'client_credentials',
                'scopes': 'full'
    }
    rsp = requests.post("https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token", data=payload)
    print(rsp.json())
    anypoint_access_token = rsp.json()['access_token']
    
    print("Access token",anypoint_access_token)
    
    if (tokenType == 'access') :
        #Return the registration response
        return {
            'statusCode': 200,
            'access_token': anypoint_access_token,
            'envId': envId,
            'orgId': orgId 
        }
    
    #Call Runtime Manager API with access token obtained in the previous call 
    #to obtain registration token
    
    armrq_headers = {
        'x-anypnt-env-id': envId, 
        'x-anypnt-org-id': orgId,
        'Authorization': 'Bearer ' + anypoint_access_token
    }
       
    
    armReqUrl = '/hybrid/api/v1/servers/registrationToken'
    conn.request('GET', armReqUrl, "", armrq_headers)
    arm_response = json.loads(conn.getresponse().read().decode())['data']
    
    
    #Return the registration response
    return {
        'statusCode': 200,
        'registration_token': json.dumps(arm_response),
        'access_token': anypoint_access_token,
        'envId': envId,
        'orgId': orgId 
    }        
    
    
#Deploy application from mule application file    
def deployAppFromFile(event, appName, targetId, applicationFile):
    armrq_headers = {
        'x-anypnt-env-id': event['envId'], 
        'x-anypnt-org-id': event['orgId'],
        'Authorization': 'Bearer ' + event.get('accessToken',"")
    }
    domain = event['domain']
    conn = http.client.HTTPSConnection(domain)
    
    armReqUrl = "/hybrid/api/v1/applications"
    
    body = {
        "artifactName": appName.strip(".jar"), 
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
    print(apiResponse)    
    arm_response = json.loads(apiResponse)['data']
    print(arm_response)
    for server in arm_response:
        if (server['name'] == serverName) :

            return {
                'statusCode': 200,
                'targetId': server['id'],
                'type' : server['type'],
                'status' : server['status']
            }


def lambda_serverGroupAction(event, context):
    domain = event['domain']
    conn = http.client.HTTPSConnection(domain)
    accessToken = event.get('accessToken',"")
    serverName = event.get('serverName')
    serverGroupName = event.get('serverGroupName')
    envId = event.get('envId')
    orgId = event.get('orgId')
    actionType = event.get('action','add')

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
    
    if (actionType == 'add'): 
        req = requests.post(url, headers=headers)
        return {
            'statusCode' : 200,
            'message' : 'server added to the group'
        }
        
    if (actionType == 'remove'):
        req = requests.delete(url, headers=headers)
        print(req)
        #Remove server
        srvDelUrl = "https://anypoint.mulesoft.com/hybrid/api/v1/servers/" + str(serverId)
        rsp = requests.delete(srvDelUrl, headers=headers)
        print(rsp)
        return {
            'statusCode' : 200,
            'message' : 'server deleted'
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
