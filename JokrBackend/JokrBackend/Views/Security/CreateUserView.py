#===============================================================================
# CreateUserView
# View to set up a new user of the app in our database.
# We use AWS Cognito to handle authorzing tokens for our anonymous users.
#
# Nick Wrobel
# Created: 7/17/15
# Modified: 2/9/15
#===============================================================================

from django.views.decorators.csrf import csrf_exempt
import simplejson as json
import logging
from django.conf import settings
from django.db import transaction
from JokrBackend.models import User
import JokrBackend.Constants as Const
from JokrBackend.Custom import HttpResponseFactory, Utils
from JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.DataCollection.DataCollector as DataCollector
import JokrBackend.Security.AuthManager as AuthManager 

logger = logging.getLogger('django')

@csrf_exempt
def CreateUser(requestData):
    TAG = Const.Tags.Urls.SECURITY_CREATE
    
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
       
    try:      
        # Create the new user identity in the db    
        with transaction.atomic():            
            newUser = User.objects.create()
            newUserID = Utils.BinaryToUUID(newUser.id)
            identityID = ''
          
            # Create a new identity on Cognito with the new uuid
            # Only when in not in DEBUG. I don't want to get charged ;)
            if (not settings.DEBUG):
                identityID = AuthManager.CreateNewCognitoIdentity(newUserID)
                
            jsonDict = _CreateUserClientObject(newUserID, identityID).getOrderedDict()         
            jsonString = json.dumps(jsonDict)
            logger.info(jsonString)
            
            # Update the URL hit and return
            DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                       responseCode=Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                       messageCode=Const.DataCollection.MessageCodes.SecurityCreate.CREATE_SUCCESSFUL)
                  
            return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                                        jsonString, 'application/json')
        
    except Exception as e:
        DataCollector.logServerError(e)
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                   responseCode=Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR,
                                   messageCode=Const.DataCollection.MessageCodes.SecurityCreate.CREATE_FAILED_SERVER_ERROR)
        
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.SecurityCreate.CREATE_FAILED_SERVER_ERROR)
        
        
    
#------------------------------------------------------------------------------ 
# This class is a wrapper for the json of initialize user to be sent to client.
#------------------------------------------------------------------------------ 
class _CreateUserClientObject:
    def __init__(self, userID, identityID):
        self.userID = userID
        self.identityID = identityID
        
    # Returns an ordered dictionary. This is 
    # necessary in order to properly json stringify the object.
    def getOrderedDict(self):
        import collections

        dict = collections.OrderedDict()
        dict[Const.Views.CreateUser.JsonResponseKey.USER_ID] = self.userID
        dict[Const.Views.CreateUser.JsonResponseKey.IDENTITY_ID] = self.identityID
        return dict
    


    
    
