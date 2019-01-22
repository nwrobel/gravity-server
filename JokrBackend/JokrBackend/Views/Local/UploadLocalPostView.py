#===============================================================================
# UploadLocalPostView
# Module/view that allows client to post to local.
#
# Nick Wrobel
# Created: 4/22/15
# Modified: 11/5/15
#===============================================================================

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.conf import settings
import time
from JokrBackend.models import LocalPost
from JokrBackend.Custom import HttpResponseFactory
from JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.Constants as Const
import JokrBackend.Custom.Utils as Utils
import JokrBackend.DataCollection.DataCollector as DataCollector
    

# CSRF requirement poses a problem, remove CSRF here.     
@csrf_exempt                        
def UploadLocalPost(requestData):
    
    TAG = Const.Tags.Urls.UPLOAD_LOCAL
    
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
    
    try:
           
        clientUser = securityProperties.clientUserObject
        clientLatitude = securityProperties.jsonRequestData[Const.Views.UploadLocalPost.JsonRequestKey.LATITUDE]
        clientLongitude = securityProperties.jsonRequestData[Const.Views.UploadLocalPost.JsonRequestKey.LONGITUDE]  
        clientPostText = securityProperties.jsonRequestData[Const.Views.UploadLocalPost.JsonRequestKey.TEXT]
        clientPostURL = securityProperties.jsonRequestData[Const.Views.UploadLocalPost.JsonRequestKey.URL]
        clientARN = securityProperties.jsonRequestData[Const.Views.UploadLocalPost.JsonRequestKey.ARN]
    
 
        # Moderation - check if this user is posting too fast
        if (settings.RATE_LIMIT_LOCAL and _UserLocalRateLimitExceeded(clientUser.id)):         
            DataCollector.logURL(TAG, { 
                Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_TOO_MANY_REQUESTS,
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.UploadLocal.RATE_LIMIT_EXCEEDED,
                Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid),
                Const.DataCollection.ParamNames.LATITUDE: clientLatitude,
                Const.DataCollection.ParamNames.LONGITUDE: clientLongitude,
                Const.DataCollection.ParamNames.HAS_TEXT: (not Utils.StringIsEmpty(clientPostText)) })
    
            return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_TOO_MANY_REQUESTS, 
                                                        Const.DataCollection.MessageCodes.UploadLocal.RATE_LIMIT_EXCEEDED)
            
    
        # Creating a localPost and saving it in the DB       
        # Create a new LocalPost and populate the fields from the Json
        newPost = LocalPost(fromUser=clientUser,
                            latitude=clientLatitude,
                            longitude=clientLongitude,
                            text=clientPostText,
                            url=clientPostURL,
                            contentType=Const.Tags.ContentTypes.LOCALPOST,
                            arn=clientARN)
        
        # If there is an exception, roll back this db transaction
        # Save the post in the database
        with transaction.atomic():
            newPost.save()
                
        # log and return on success
        DataCollector.logURL(TAG, { 
            Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK,
            Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.UploadLocal.POST_SUCCESSFUL,
            Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid),
            Const.DataCollection.ParamNames.LATITUDE: clientLatitude,
            Const.DataCollection.ParamNames.LONGITUDE: clientLongitude,
            Const.DataCollection.ParamNames.HAS_TEXT: (not Utils.StringIsEmpty(clientPostText)) })   
           
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                                    Const.DataCollection.MessageCodes.UploadLocal.POST_SUCCESSFUL)
        
    except Exception as e:
        # log and return on error
        DataCollector.logServerError(e)
        DataCollector.logURL(TAG, { 
            Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR,
            Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.UploadLocal.POST_FAILED_SERVER_ERROR,
            Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid),
            Const.DataCollection.ParamNames.LATITUDE: clientLatitude,
            Const.DataCollection.ParamNames.LONGITUDE: clientLongitude,
            Const.DataCollection.ParamNames.HAS_TEXT: (not Utils.StringIsEmpty(clientPostText)) })
        
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.UploadLocal.POST_FAILED_SERVER_ERROR)

#-------------------------------------------------------------------------------
# _UserLocalRateLimitExceeded
# Checks if the user is posting too fast to local, for moderation
# 
# params:
#    clientUserID - uuid of the client
# returns:
#     T/F if the user has posted too fast and needs to wait
#-------------------------------------------------------------------------------
def _UserLocalRateLimitExceeded(clientUserID):
    
    currentTime = time.time()
    
    # Get all the timestamps for localposts, as a flat list    
    postTimes = LocalPost.objects.values_list('timeCreated', flat=True) 
    postTimes = postTimes.filter(fromUser=clientUserID) # only from this user
    # order by time created, descending. Limit to the max # of replies we want to examine
    postTimes = postTimes.order_by('-timeCreated')[:Const.Views.UploadLocalPost.MAX_POSTS_WITHIN_TIMEFRAME] 

    # If there are at least x posts, check the min of the set against the current time
    if len(postTimes) == Const.Views.UploadLocalPost.MAX_POSTS_WITHIN_TIMEFRAME:
        minPostTime = min(list(postTimes))
        timeToleranceSeconds = Const.Views.UploadLocalPost.TIMEFRAME_MINUTES * 60
        if (currentTime - minPostTime) < timeToleranceSeconds:
            return True
    
    # else
    return False
    
