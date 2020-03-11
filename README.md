# muleautoscaling
Infotiate Mule Auto Scaling is a serverless solution that enables auto scaling support for mule runtimes running on AWS in hybrid mode. With autscaling support you can now run mule runtimes as part of an auto scaling group and scale up or down your workloads based on scaling policies. This also gives tremendous flexibility to make use of cloud native features such as dynamic scaling, use of spot instances to run mule workloads 

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
