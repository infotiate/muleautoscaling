
import mulefunctions

def lambda_handler(event, context):
    print(event)
    tokRsp = mulefunctions.lambda_getArmAccessToken(event)
    print(tokRsp)
    return tokRsp
