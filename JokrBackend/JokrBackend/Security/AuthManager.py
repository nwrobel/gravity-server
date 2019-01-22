#-------------------------------------------------------------------------------
# Module for managing general authentication and token related procedures.
# 
# Nick Wrobel
# Created: 1/5/16
# Modified: 1/5/16
#-------------------------------------------------------------------------------

import time
import boto3
from django.conf import settings
from django.db import transaction
import JokrBackend.Constants as Const

#-------------------------------------------------------------------------------
# Creates a new AWS Cognito identity from a uuid
# 
# Params:
#    newUUID - the uuid from which to create the new identity
# Returns:
#    the amazon identity ID (Amazon's way of identifying this user)
#-------------------------------------------------------------------------------
def CreateNewCognitoIdentity(newUUID):
    client = boto3.client('cognito-identity', region_name=settings.AWS_REGION_NAME)
    
    # Create a new identity with the new uuid we generated
    response = client.get_open_id_token_for_developer_identity(
        IdentityPoolId=settings.AWS_COGNITO_IDENTITY_POOL_ID,
        Logins={ settings.AWS_COGNITO_DEVELOPER_PROVIDER_NAME : newUUID },
        TokenDuration=settings.AWS_COGNITO_TOKEN_DURATION 
    )
    
    return response['IdentityId']
    

#-------------------------------------------------------------------------------
# Logs in a user, given the user's uuid (which is also the AWS Cognito UUID)
# 
# Params:
#    uuid - the user's uuid
# Returns:
#    token - the authentication token that the client 
#-------------------------------------------------------------------------------
def LoginWithCognitoIdentity(uuid):
    
    client = boto3.client('cognito-identity', region_name=settings.AWS_REGION_NAME)
    
    response = client.get_open_id_token_for_developer_identity(
        IdentityPoolId=settings.AWS_COGNITO_IDENTITY_POOL_ID,
        Logins={ settings.AWS_COGNITO_DEVELOPER_PROVIDER_NAME : str(uuid) },
        TokenDuration=settings.AWS_COGNITO_TOKEN_DURATION 
    )
    
    token = response['Token']
    return token