#===============================================================================
# AnalyticsFeedbackView
# Allows the client to submit feedback, which is used for analytics.
#
# Nick Wrobel
# Created: 2/10/15
# Modified: 2/10/15
#===============================================================================

from django.views.decorators.csrf import csrf_exempt
from JokrBackend.models import Feedback
import JokrBackend.Constants as Const
from JokrBackend.Custom import HttpResponseFactory
from JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.DataCollection.DataCollector as DataCollector

        
@csrf_exempt
def AnalyticsFeedback(requestData):
    TAG = Const.Tags.Urls.ANALYTICS_FEEDBACK
    
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
       
    try:      
        clientFeedbackText = securityProperties.jsonRequestData[Const.Views.AnalyticsFeedback.JsonRequestKey.TEXT]
          
        # Save the feedback in the DB
        Feedback.objects.create(fromUser=securityProperties.userObject,
                                text=clientFeedbackText)
            
        # Update the URL hit and return
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                    responseCode=Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                    messageCode=Const.DataCollection.MessageCodes.AnalyticsFeedback.REQUEST_SUCCESSFUL)
                  
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                                    Const.DataCollection.MessageCodes.AnalyticsFeedback.REQUEST_SUCCESSFUL)
        
    except Exception as e:
        DataCollector.logServerError(e)
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                   responseCode=Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR,
                                   messageCode=Const.DataCollection.MessageCodes.AnalyticsFeedback.REQUEST_FAILED_SERVER_ERROR)
        
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.AnalyticsFeedback.REQUEST_FAILED_SERVER_ERROR)
        
        
    
    


    
    
