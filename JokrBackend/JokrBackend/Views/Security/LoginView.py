#-------------------------------------------------------------------------------
# Login view
# Allows a user to login to our servers and receive a temporary access token
# This URL essentially serves as our own identity provider
#
# Nick Wrobel
# Created: 12/17/15
# Modified: 2/9/16
#-------------------------------------------------------------------------------

import time
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import simplejson as json
import JokrBackend.Constants as Const
from JokrBackend.Custom import HttpResponseFactory, Utils
from JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.DataCollection.DataCollector as DataCollector
import JokrBackend.Security.AuthManager as AuthManager 
from JokrBackend.models import Session

   
@csrf_exempt
def Login(requestData):
    TAG = Const.Tags.Urls.SECURITY_LOGIN

    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
    
    try:   
        currentTime = int(time.time())
        timeSessionExpires = currentTime + settings.AWS_COGNITO_TOKEN_DURATION
        
        # Get the client user 
        clientUser = securityProperties.userObject
        
        # Login to Cognito and retrieve the access token for this client
        # We login with our uuid
        token = AuthManager.LoginWithCognitoIdentity(securityProperties.userID)
        
        # Create a new user session in the DB
        Session.objects.create(fromUser=securityProperties.userObject,
                               timeExpires=timeSessionExpires,
                               token=token)       

                    
        jsonString = json.dumps(_LoginClientObject(token).getOrderedDict())

        DataCollector.UpdateURLHit(hitID=securityProperties.hitID, 
                                   responseCode=Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                   messageCode=Const.DataCollection.MessageCodes.SecurityLogin.REQUEST_SUCCESSFUL)
          
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                                    jsonString, 'application/json')
        
    except Exception as e:
        DataCollector.logServerError(e)
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID, 
                                   responseCode=Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                   messageCode=Const.DataCollection.MessageCodes.SecurityLogin.REQUEST_FAILED_SERVER_ERROR)
         
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.SecurityCreate.CREATE_FAILED_SERVER_ERROR)


#------------------------------------------------------------------------------ 
# This class is a wrapper for the json to be sent to client.
#------------------------------------------------------------------------------ 
class _LoginClientObject:
    def __init__(self, token):
        self.token = token
        
    # Returns an ordered dictionary. This is 
    # necessary in order to properly json stringify the object.
    def getOrderedDict(self):
        import collections

        dict = collections.OrderedDict()
        dict[Const.Views.SecurityLogin.JsonResponseKey.TOKEN] = self.token
        return dict




    
