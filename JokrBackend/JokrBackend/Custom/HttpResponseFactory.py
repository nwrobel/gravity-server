#-------------------------------------------------------------------------------
# HttpResponse Factory module
# Used to create and return HttpResponse object to views that need them.
# Abstracts the need to worry about response codes, in some cases.
# Also, only returns a message if the setting is on, to prevent giving hackers
# any information, while still providing useful debugging messages.
#
# Nick Wrobel
# Created: 9/24/15
# Modified: 12/16/15
#-------------------------------------------------------------------------------

from django.http import HttpResponse
from django.conf import settings
import JokrBackend.Constants as Const
import JokrBackend.Custom.Utils as Utils

#-------------------------------------------------------------------------------
# MakeSecurityErrorHttpResponse
# Method to examine a security properties object and return the correct 
# response code and message.
#
# Params:
#     securityProperties - security properties object
# Returns:
#    securityHttpResponse - the proper HttpResponse
#-------------------------------------------------------------------------------
def MakeSecurityErrorHttpResponse(securityProperties):

    securityHttpResponse = HttpResponse()
    errorsList = securityProperties.errorsList
    
    # Set the appropriate status code, given the security error
    
    # 404
    if (Const.DataCollection.MessageCodes.Security.URL_NOT_FOUND in errorsList):
        securityHttpResponse.status_code = Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_NOT_FOUND
    
    # 401 (unauthorized)
    # Session token expired, bad, or missing
    # or userID is bad or missing
    elif (Const.DataCollection.MessageCodes.Security.NO_CLIENT_ID in errorsList or
          Const.DataCollection.MessageCodes.Security.BAD_CLIENT_ID in errorsList or
          Const.DataCollection.MessageCodes.Security.NO_SESSION_TOKEN in errorsList or
          Const.DataCollection.MessageCodes.Security.BAD_SESSION_TOKEN in errorsList or
          Const.DataCollection.MessageCodes.Security.EXPIRED_SESSION in errorsList):
        securityHttpResponse.status_code = Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_UNAUTHORIZED

    # User is banned   
    elif (Const.DataCollection.MessageCodes.Security.BANNED_FROM_SERVICE in errorsList):
        securityHttpResponse.status_code = Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_FORBIDDEN       

    # Bad request method
    elif (Const.DataCollection.MessageCodes.Security.BAD_REQUEST_METHOD in errorsList):
        securityHttpResponse.status_code = Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_METHOD_NOT_ALLOWED
    
    # Bad content-type 
    elif (Const.DataCollection.MessageCodes.Security.BAD_CONTENT_TYPE in errorsList):
        securityHttpResponse.status_code = Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_UNSUPPORED_CONTENT_TYPE
    
    # Bad request (a client data error)
    elif (Const.DataCollection.MessageCodes.Security.MALFORMED_JSON in errorsList or 
          Const.DataCollection.MessageCodes.Security.WRONG_NUMBER_JSON_PARAMS in errorsList or
          Const.DataCollection.MessageCodes.Security.INVALID_JSON_PARAMS in errorsList):
        securityHttpResponse.status_code = Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_BAD_REQUEST
        
    # Data validation failure 
    elif (Const.DataCollection.MessageCodes.Security.DATA_VALIDATION_FAIL in errorsList):
        securityHttpResponse.status_code = Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_UNPROCESSABLE_ENTITY

    # Otherwise, there is a bug 
    else:
        securityHttpResponse.status_code = Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR
    
    # Send the list of security errors, if HTTP response messages are enabled
    if (settings.HTTP_RESPONSE_MESSAGES):               
        securityHttpResponse.content = Utils.ListToCSV(errorsList)
        
    return securityHttpResponse
  
#-------------------------------------------------------------------------------
# MakeHttpResponse
# Method to make an HttpResponse given the params.
#
# Params:
#    responseCode - the desired status code to return
#    content - the content payload to be delivered 
#    contentType - (optional) the content-type header
# Returns:
#    the HttpResponse
#-------------------------------------------------------------------------------
def MakeHttpResponse(responseCode, content, contentType=None):
    response = HttpResponse()
    if (settings.HTTP_RESPONSE_MESSAGES):
        response.content = content
    response.status_code = responseCode
    
    if (contentType is not None):
        response['Content-Type'] = contentType

    return response
    
        