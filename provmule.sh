#!/bin/bash
MULE_HOME=/home/ec2-user/mule-enterprise-standalone-4.2.2
USR_HOME=/home/ec2-user
LAMDA_ACCESS_TOK=sam_muleGetAccessToken
LAMBDA_SRV_GROUP=sam_muleServerGroupAction
REGION=us-east-1
unzip $USR_HOME/mule-ee-distribution-standalone-4.2.2.zip -d $USR_HOME
echo "Checking existing installation..."
AGENT_FILE=$MULE_HOME/conf/mule-agent.yml
if [ -f "$AGENT_FILE" ]; then
	echo "Error! Server already registered"
	exit -1
fi
echo "Obtaining Registration Token..."
REGISTRATION_RESPONSE=$(aws lambda invoke --region $REGION --function-name $LAMDA_ACCESS_TOK  --payload '{"region": "us-east-1"}' response.json)
REG_TOK=$(cat response.json | python -c "import sys, json; print json.load(sys.stdin)['registration_token'].strip('\"')")
echo "Registration Token -> " $REG_TOK
echo "******************************"
echo "Setting up Mule Agent...."
echo "******************************"
INSTANCE_ID=$(wget -q -O - http://169.254.169.254/latest/meta-data/instance-id)
echo "Instance ID " $INSTANCE_ID
$MULE_HOME/bin/amc_setup -H $REG_TOK $INSTANCE_ID
echo "Starting mule runtime..."
$MULE_HOME/bin/mule start
echo "Setup done."
#####################################
echo "Adding server to the group"
ACCESS_TOK=$(cat response.json | python -c "import sys, json; print json.load(sys.stdin)['access_token']")
ENV_ID=$(cat response.json | python -c "import sys, json; print json.load(sys.stdin)['envId']")
ORG_ID=$(cat response.json | python -c "import sys, json; print json.load(sys.stdin)['orgId']")
echo '{"accessToken":' '"'${ACCESS_TOK}'"' ',"serverGroupName": "MuleRuntimesDev","domain": "anypoint.mulesoft.com","serverName":' '"'${INSTANCE_ID}'"' ',"envId":' '"'${ENV_ID}'"' ',"orgId":''"'${ORG_ID}'"}' > payload.json
cat payload.json

SERVERGRP_RESPONSE=$(aws lambda invoke --region $REGION --function-name $LAMBDA_SRV_GROUP  --payload file://payload.json  response_svg.json)

cat response_svg.json
