#-------------------------------------------------------------------------------
# SecurityChecker 
# This module contains methods that check for security errors in any incoming 
# URL (including those that are a 404). Think of this as the security guard
# checking your ID when you enter the building.
#
# Nick Wrobel
# Created: 9/24/15
# Modified: 12/16/15 
#-------------------------------------------------------------------------------

import time
import collections
from django.core.exceptions import ObjectDoesNotExist
import simplejson as json
from django.db import transaction
import JokrBackend.Constants as Const
import JokrBackend.Custom.Utils as Utils
from JokrBackend.models import User, Session
from JokrBackend.Security.SecurityProperties import SecurityProperties
from JokrBackend.Security import SecurityActuator
import JokrBackend.Security.DataValidator as DataValidator
from JokrBackend.Custom.HttpResponseFactory import MakeSecurityErrorHttpResponse
from JokrBackend.DataCollection import DataCollector, QueryManager

#------------------------------------------------------------------------------ 
# RunThroughSecurityLayer
# Runs the request data for a URL through the security layer.
# Does a low level security check and then a data validation check.
# If there is a security issue, then the SecurityActuator module is called
# to take action.
# 
# params: 
#    urlName - the name of the URL, should be a constant (404 name if the url is a 404)
#    urlRequestData - the raw url request data handed down from the View
# returns: 
#     securityProperties - an object with various properties
#------------------------------------------------------------------------------ 
def RunThroughSecurityLayer(urlTag, urlRequestData):
    currentTime = time.time()
    
    # Get all security info on this request
    securityProperties = SecurityProperties()
    securityProperties = GetData(securityProperties, urlTag, urlRequestData, currentTime)
    securityProperties = CheckData(securityProperties, urlTag)
    securityProperties = CheckUserIdentity(securityProperties, urlTag, currentTime)
    
    # Once all checks are done, set is isSecure flag
    if (securityProperties.errorsList):
        securityProperties.isSecure = False
    else:
        securityProperties.isSecure = True
    
    # Attach an appropriate Http response that we can use, if there was an error
    if (not securityProperties.isSecure):
        securityProperties.httpResponse = MakeSecurityErrorHttpResponse(securityProperties)
    
    # Log the request 
    # This also logs security errors if there are any
    # and returns the hitID for the hit so we can use it later
    securityProperties.hitID = DataCollector.LogURLHit(securityProperties)
        
    return securityProperties

#-------------------------------------------------------------------------------
# GetData
# Grabs the metadata from the raw request data and put its on the object
# Low level - simply gets the data
# 
# Returns:
#     the updated securityProperties object, with the metadata attached
#-------------------------------------------------------------------------------
def GetData(securityProperties, urlTag, urlRequestData, currentTime):
    
    clientIP = _GetIPAddress(urlRequestData) 
    requestMethod = urlRequestData.method
    requestedURL = urlRequestData.path
    requestContentType = ''
    requestData = urlRequestData.read().decode()   
    userID = ''
    sessionToken = ''
    
    # Grab our custom header values (if they exist)
    if (Const.Headers.USERID_HEADER_NAME in urlRequestData.META):
        userID = urlRequestData.META[Const.Headers.USERID_HEADER_NAME]
        
    if (Const.Headers.SESSION_TOKEN_HEADER_NAME in urlRequestData.META):
        sessionToken = urlRequestData.META[Const.Headers.SESSION_TOKEN_HEADER_NAME]

    if ('CONTENT_TYPE' in urlRequestData.META):
        requestContentType = urlRequestData.META['CONTENT_TYPE']    
              
    # Attach data to our object
    securityProperties.timestamp = int(currentTime)
    securityProperties.clientIP = clientIP
    securityProperties.requestMethod = requestMethod
    securityProperties.requestedURL = requestedURL
    securityProperties.requestContentType = requestContentType
    securityProperties.requestData = requestData
    securityProperties.userID = userID
    securityProperties.sessionToken = sessionToken
    
    return securityProperties

#-------------------------------------------------------------------------------
# CheckData
# Examines the metadata and json data and checks for security errors related
# only to the request. Updates these errors on the security properties object.
# 
# Returns:
#     the updated securityProperties object, with the errors and metadata
#-------------------------------------------------------------------------------
def CheckData(securityProperties, urlTag):  
    
    # Check for 404
    if (urlTag == Const.Tags.Urls.HANDLER_404):
        securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.URL_NOT_FOUND)

    # Check request method
    if (not _RequestMethodIsValid(securityProperties.requestMethod)):
        securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.BAD_REQUEST_METHOD)
       
    # Check the content type header
    if (not _ContentTypeIsValid(securityProperties.requestContentType)):
        securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.BAD_CONTENT_TYPE)
        
    # Check the json data
    # If it is not malformed, then save it and continue
    jsonSyntaxCheck = _CheckJsonDataForSyntax(securityProperties.requestData)
    if (not jsonSyntaxCheck.jsonIsValid):
        securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.MALFORMED_JSON)
    else:
        securityProperties.jsonRequestData = jsonSyntaxCheck.jsonData
                             
        # Check if the json params are valid
        jsonParamsCheck = _CheckJsonParams(urlTag, securityProperties.jsonRequestData)
        if (jsonParamsCheck.wrongNumParams):
            securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.WRONG_NUMBER_JSON_PARAMS)
                 
        elif (jsonParamsCheck.invalidParams):
            securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.INVALID_JSON_PARAMS)
            
        # if the json params were valid, then continue with data validation
        else:
            dataIsValid = DataValidator.DataIsValidForURL(urlTag, securityProperties.jsonRequestData)          
            if (not dataIsValid):
                securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.DATA_VALIDATION_FAIL)
    
    return securityProperties

#-------------------------------------------------------------------------------
# CheckUserIdentity
# Examines the user/session of the request and handles security procedures 
# related to user identities, phones, and authentication
#
# Returns:
#    the updated securityProperties object, with errors and 
#    the user object attached
#-------------------------------------------------------------------------------
def CheckUserIdentity(securityProperties, urlTag, currentTime):
        
    # /security/login/ requires the user's UUID parameter
    if (urlTag == Const.Tags.Urls.SECURITY_LOGIN): 

        # Get the user object from the DB        
        try: 
            # If the client supplied a userID,
            if (securityProperties.userID):
                # Get the user object using the userID
                securityProperties.userObject = QueryManager.GetObjectByID(User, securityProperties.userID)
            
            # Otherwise, log the error as having a blank uuid
            else:
                securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.NO_CLIENT_ID)
                  
        # this means the uuid was not in the DB
        except ObjectDoesNotExist:
            securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.BAD_CLIENT_ID)
    
    # Otherwise, check the session using the session token
    # The session token is required for all URLs except:
    #    /security/create/
    #    /security/login/
    elif (urlTag != Const.Tags.Urls.SECURITY_CREATE):  
        try:  
            # If the client supplied a session token,
            if (securityProperties.sessionToken):               
                # Get the user session from the token
                userSession = Session.objects.get(token=securityProperties.sessionToken)
            
                # Check if the session is expired. If so, log the error
                if (userSession.timeExpires <= currentTime):
                    securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.EXPIRED_SESSION)
   
                # Save the user object and user session 
                securityProperties.userObject = userSession.fromUser
                securityProperties.userSession = userSession
            
            # Otherwise, if no token, log the error
            else:
                securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.NO_SESSION_TOKEN)
        
        # If the user's token was not in the database at all, log the error
        except ObjectDoesNotExist:
            securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.BAD_SESSION_TOKEN)

                
    # Check if this user is banned from this url/service
    if (_UserIsBannedFromURL(urlTag, securityProperties.userObject)):
        securityProperties.errorsList.append(Const.DataCollection.MessageCodes.Security.BANNED_FROM_SERVICE)
                 
    return securityProperties

#-------------------------------------------------------------------------------
# _RequestMethodIsValid
# Checks if the request method is valid
#
# params: 
#    requestMethod - the method used in the request
# returns:
#    T/F if the request method is valid
#-------------------------------------------------------------------------------
def _RequestMethodIsValid(requestMethod):
    return (requestMethod == 'POST')
        
#-------------------------------------------------------------------------------
# _ContentTypeIsValid
# Checks if the content-type header used is valid
#
# params: 
#    contentType - the content type header used
# returns:
#    T/F if the content type is valid
#-------------------------------------------------------------------------------
def _ContentTypeIsValid(contentType):
    return ('application/json' in contentType)
          
#-------------------------------------------------------------------------------
# _UserIsBannedFromURL
# Checks to make sure the user is allowed to access this particular URL/service,
# taking into account bans
#-------------------------------------------------------------------------------
def _UserIsBannedFromURL(urlTag, user):
    
#     # All users, even if banned, can use these urls. 
#     # All others require us to check
#     # Also check that the user is not null
#     if (urlTag != Const.Tags.Urls.SECURITY_CREATE and 
#         urlTag != Const.Tags.Urls.SECURITY_LOGIN and 
#         urlTag != Const.Tags.Urls.SECURITY_GETBANINFO and 
#         user):
#         return Utils.UserIsBanned(user)
#     else:
#         return False
    return False
    
#-------------------------------------------------------------------------------
# _CheckJsonDataForSyntax
# Tries to decode the json data. Checks that json is valid syntactically
#
# params: 
#    decodedRequestData - decoded request data for the URL
# returns:
#    a named tuple: (jsonIsValid, jsonData)
#-------------------------------------------------------------------------------
def _CheckJsonDataForSyntax(decodedRequestData):
    checkResult = collections.namedtuple('check', ['jsonIsValid', 'jsonData'])
    
    try:
        decodedJsonData = json.loads(decodedRequestData) 
        return checkResult(jsonIsValid=True, jsonData=decodedJsonData)
    
    # this means the json could not be loaded (invalid)
    except ValueError:
        return checkResult(jsonIsValid=False, jsonData=None)
      
#-------------------------------------------------------------------------------
# _CheckJsonParams
# Checks whether or not the json keys that were sent are valid or not 
#
# params: 
#    urlName - the name of the URL
#    decodedRequestData - the decoded json dictionary
# returns:
#    a named tuple: ('wrongNumParams', 'invalidParams')
#-------------------------------------------------------------------------------
def _CheckJsonParams(urlTag, decodedRequestData):
    checkResult = collections.namedtuple('check', ['wrongNumParams', 'invalidParams'])

    # Check that there are no extra json parameters
    requiredParams = _GetRequiredParamsList(urlTag)
    requiredParamsLength = int(len((requiredParams)))
    actualParamsLength = int(len(list(decodedRequestData)))

    if requiredParamsLength != actualParamsLength:
        return checkResult(wrongNumParams=True, invalidParams=True)
    
    # Check that all required parameters are present
    for param in requiredParams:
        try:
            decodedRequestData[param]
        except KeyError:
            return checkResult(wrongNumParams=False, invalidParams=True)

    return checkResult(wrongNumParams=False, invalidParams=False)

#-------------------------------------------------------------------------------
# _GetRequiredParamsList
# Private method to return the list of required json parameters for one of 
# our valid URLs. Simply a constant lookup.
#
# params: 
#     urlName - name of the URL
# returns: 
#     list of strings representing the required json keys
#-------------------------------------------------------------------------------
def _GetRequiredParamsList(urlTag):
    if (urlTag == Const.Tags.Urls.SECURITY_CREATE):
        return Const.Views.CreateUser.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.UPLOAD_LOCAL):
        return Const.Views.UploadLocalPost.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.GET_LOCAL):
        return Const.Views.GetLocalPost.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.UPLOAD_MESSAGE):
        return Const.Views.UploadMessage.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.GET_MESSAGE):
        return Const.Views.GetMessage.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.MODERATION_BLOCK):
        return Const.Views.Block.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.MODERATION_REPORT):
        return Const.Views.Report.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.UPLOAD_LIVE):
        return Const.Views.UploadThread.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.GET_LIVE):
        return Const.Views.GetThread.REQUIRED_PARAMS
      
    elif (urlTag == Const.Tags.Urls.UPLOAD_REPLY):
        return Const.Views.UploadReply.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.GET_REPLY):
        return Const.Views.GetReply.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.ANALYTICS_FEEDBACK):
        return Const.Views.AnalyticsFeedback.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.SUBSCRIBE_LIVE):
        return Const.Views.SubscribeLive.REQUIRED_PARAMS
    
    elif (urlTag == Const.Tags.Urls.UNSUBSCRIBE_LIVE):
        return Const.Views.UnsubscribeLive.REQUIRED_PARAMS
    
    return ''

#-------------------------------------------------------------------------------
# GetIPAddress
# Returns the IP address from the request data
#-------------------------------------------------------------------------------
def _GetIPAddress(requestData):
    
    # Try getting the IP the normal way django expects
    ipAddress = requestData.META['REMOTE_ADDR']

    # If it is screwed up (happens with Nginx), then we need to add the 
    # 'HTTP_' prefix to the header key
    if (ipAddress == "b''"):
        ipAddress = requestData.META['HTTP_REMOTE_ADDR']
                                                                                
    return ipAddress


    
    



    
    
    
    
    
    
     
