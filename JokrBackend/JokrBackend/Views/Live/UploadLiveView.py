#===============================================================================
# UploadThreadView
# View that lets a client create a new piece of content on live.
#
# Nick Wrobel
# Created: 7/20/15
# Modified: 2/15/16
#===============================================================================

from django.views.decorators.csrf import csrf_exempt
import JokrBackend.Custom.Utils as Utils
from django.conf import settings
from JokrBackend.models import Thread
import JokrBackend.Constants as Const
from JokrBackend.Custom import HttpResponseFactory
from JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.DataCollection.DataCollector as DataCollector
from JokrBackend.Views.Live.GetLiveView import GetThreadListJsonString
import JokrBackend.DataCollection.QueryManager as QueryManager
import JokrBackend.Security.RateLimiter as RateLimiter

@csrf_exempt
def UploadLive(requestData):
    TAG = Const.Tags.Urls.UPLOAD_LIVE

    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
    
    try:       
        clientUser = securityProperties.userObject
        clientSession = securityProperties.userSession
        clientThreadText= securityProperties.jsonRequestData[Const.Views.UploadThread.JsonRequestKey.THREAD_TEXT]
        clientThreadKey = securityProperties.jsonRequestData[Const.Views.UploadThread.JsonRequestKey.THREAD_URL]
        clientThreadARN = securityProperties.jsonRequestData[Const.Views.UploadThread.JsonRequestKey.THREAD_ARN]
 
        # check if this user is posting too fast
        if (settings.RATE_LIMIT_LIVE and RateLimiter.UserLiveRateLimitExceeded(clientUser.id)): 
                  
            # log the warning and return if too many threads
            DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                       responseCode=Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_TOO_MANY_REQUESTS, 
                                       messageCode=Const.DataCollection.MessageCodes.UploadLive.RATE_LIMIT_EXCEEDED)

            return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_TOO_MANY_REQUESTS, 
                                                        Const.DataCollection.MessageCodes.UploadLive.RATE_LIMIT_EXCEEDED) 

        # Save the live thread in the DB
        # Save title as an empty string if it is empty
        if (Utils.StringIsEmpty(clientThreadText)):
            clientThreadText = ''
               
        Thread.objects.create(fromUser=clientUser,
                              fromSession=clientSession,
                              contentType=Const.Tags.ContentTypes.THREAD,
                              text=clientThreadText,
                              key=clientThreadKey,
                              arn=clientThreadARN)
                     

        QueryManager.CheckAndPruneThreads()           
       
        # FOR RELEASE 1.1
        # return the list of threads after a successful thread upload    
        jsonString = GetThreadListJsonString()

        # log and return on success   
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                    responseCode=Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                    messageCode=Const.DataCollection.MessageCodes.UploadLive.POST_SUCCESSFUL)         
       
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                                    jsonString, 'application/json')
        
    except Exception as e:
        DataCollector.logServerError(e)
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                    responseCode=Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                    messageCode=Const.DataCollection.MessageCodes.UploadLive.POST_FAILED_SERVER_ERROR)  

        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.UploadLive.POST_FAILED_SERVER_ERROR)



            

    



            
            
    
    
    