import logging
import mulefunctions

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def lambda_serverGroupAction(event, context):
    LOGGER.debug('Callging server group action with ')
    LOGGER.debug(event)
    response = mulefunctions.lambda_serverGroupAction(event, context)
    LOGGER.debug("Server group action response..")
    LOGGER.debug(response)
    return response

