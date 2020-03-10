#!/bin/bash
TEMPLATE_FILE=$1
STACK_NAME=$2
SAM_S3BUCKET=$3
REGION=$4
PARAM_MULE_CODE_BUCKET=$5
PARM_SECRET_ARN=$6

sam deploy --template-file $TEMPLATE_FILE  --stack-name $STACK_NAME --s3-bucket $SAM_S3BUCKET --region $REGION --capabilities CAPABILITY_IAM --parameter-overrides MuleCodeS3BucketArn=$PARAM_MULE_CODE_BUCKET SecretArn=PARM_SECRET_ARN


