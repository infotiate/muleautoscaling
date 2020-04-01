# muleautoscaling
Infotiate Mule Auto Scaling is a serverless solution that enables auto scaling support for mule runtimes running on AWS in hybrid mode. With autscaling support you can now run mule runtimes as part of an auto scaling group and scale up or down your workloads based on scaling policies. This also gives tremendous flexibility to make use of cloud native features such as dynamic scaling, use of spot instances to run mule workloads 

**Solution overview** is available at our [Wiki](https://github.com/infotiate/muleautoscaling/wiki) page

**Note: Documenation is not fully updated yet so pelase email us at info@infotiate.com in case you need help**

# Installation

## Create Anypoint connected App or Anypoint account

Please read [Mulesoft documentation on how to create connected app in you Anypoint account](https://docs.mulesoft.com/access-management/connected-apps-overview). Following scopes needs to be enabled on the connected App 
- **Runtime Manager**
    - Read Servers
    - Manage Servers
    - Read Applications
    - Create Applications
- **General**
    - View Organizations
    - Profile

>We recommend you use connected app client id and secret over Anypoint user and password for obvious security reasons. Apart from above you'll also need Organization ID and Environment ID of your Anypoint environment

You'll need this client ID, Client Secret, Organization ID and Environment ID and  later when you create secret in AWS Secrets Manager so take a note of client id and secret

## Create Secret

> AWS Secrets Manager helps you protect secrets needed to access your applications, services, and IT resources. The service enables you to easily rotate, manage, and retrieve database credentials, API keys, and other secrets throughout their lifecycle. Users and applications retrieve secrets with a call to Secrets Manager APIs, eliminating the need to hardcode sensitive information in plain text. Please refer to AWS [Secrets Manager documentation to](https://aws.amazon.com/secrets-manager/) learn how to create Secret in AWS Secrets Manager

Create secret in AWS Secrets manager and name the secret as **MuleAnypointUser** with following values
- **muleDomainUrl** - (Required) for example anypoint.mulesoft.com 
- **envId** - (Required) Environment ID
- **orgId** - (Required) Organization ID
- **client_id** (Created when connected app is configured on Anypoint cloud hub console)
- **client_secret** (Created when connected app is configured on Anypoint cloud hub console)
- **ap_auth_method** - (Required) Anypoint Authentication method, specify following options
	- **oauth** - for connected app authentication using client id and secret
	- **user** - for Anypoint user name using user id and password
- **muleAnypointUser** - Anypoint user name (Optional)
- **muleAnypointUserPassword** - User password 

Take note of the ARN of the secret as you'll need it later when we build and deploy AWS SAM (Serverless Application Module) template

## Deployment setup

### Launch an Amazon Linux 2 instance with following software installed
 - Git
 - AWS CLI
 - AWS SAM CLI
 - Python 3.8 or 3.7
 - Open JDK 8, required to run mule runtime
 - Download and copy the mule runtime on to the instance. By default the [user data script](https://github.com/infotiate/muleautoscaling/blob/master/provmule.sh) assume in /home/ec2-user directory e.g. /home/ec2-user/mule-enterprise-standalone-4.2.2.zip. We recommend you modify the location of MULE_HOME and USER_HOME and the AWS region as per your configuration preferences
 - Clone the [git repository](https://github.com/infotiate/muleautoscaling) in the directory of your choice
 - Create s3 bucket for storing aws sam packaged code
 - Switch to the directory where you clone the git repository and **sam build** command. This will build the code
 - Execute **[package.sh
 ](https://github.com/infotiate/muleautoscaling/blob/master/package.sh)** script and pass s3 bucket name created above. this will package the code and copy the code in the s3 bucket and generate the packaged.yaml file 
 - Execute **deploy.sh**
 
 ```
 
 #!/bin/bash
TEMPLATE_FILE=$1 <- packeged.yml file created by package.sh script
STACK_NAME=$2 <- specify stack name you want
SAM_S3BUCKET=$3 <- specify the same s3 bucket that is passed to package.sh script
REGION=$4 <- AWS region
PARAM_MULE_CODE_BUCKET=$5 <- s3 bucket ARN where mule application archives are stored
PARM_SECRET_ARN=$6 <- ARN of the AWS secret

sam deploy --template-file $TEMPLATE_FILE --stack-name $STACK_NAME --s3-bucket $SAM_S3BUCKET --region $REGION --capabilities CAPABILITY_IAM --parameter-overrides MuleCodeS3BucketArn=$PARAM_MULE_CODE_BUCKET SecretArn=PARM_SECRET_ARN`

```
 - The deploy.sh will create lambda resources

### Create Mule Runtime AMI
Launch an Amazon Linux 2 instance with following software installed
 - Python 3.8 or 3.7
 - Open JDK 8, required to run mule runtime
 - Download and copy the mule runtime on to the instance. By default the [user data script](https://github.com/infotiate/muleautoscaling/blob/master/provmule.sh) assume in /home/ec2-user directory e.g. /home/ec2-user/mule-enterprise-standalone-4.2.2.zip. We recommend you modify the location of MULE_HOME and USER_HOME and the AWS region as per your configuration preferences
 ```
 You need to update following in user data script as per your configuration
 
 1) If you have the enterprise license the update user data script to include commands to install enterprise license. More details regarding how to install license can be found at https://docs.mulesoft.com/mule-runtime/4.2/installing-an-enterprise-license
 
 2) Change the region name in the following line of code default is **us-east-1**
 REGISTRATION_RESPONSE=$(aws lambda invoke --region $REGION --function-name $LAMDA_ACCESS_TOK  --payload '{"region": "us-east-1"}'  response.json)
 
 3) Chnage the server group name, default is **MuleRuntimeDev**
 echo '{"accessToken":' '"'${ACCESS_TOK}'"' ',"serverGroupName": "MuleRuntimesDev","domain": "anypoint.mulesoft.com","serverName":' '"'${INSTANCE_ID}'"' ',"envId":' '"'${ENV_ID}'"' ',"orgId":''"'${ORG_ID}'"}' > payload.json
cat payload.json

 
 ```
 - Create AMI
 - Create Instance profiel IAM role and provide access to 
   - **lambda:InvokeFunction** to the Lambda functions created by deploy.sh script
 - Launch EC2 instance with above AMI and specify **provmule.sh** as user data script and the instanc eprofile created above as instance role. Please make sure to modify the script as per your configuration
 
