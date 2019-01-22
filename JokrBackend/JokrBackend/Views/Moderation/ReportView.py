#------------------------------------------------------------------------------ 
# ReportView
# Allows client to report a piece of content.
#
# Nick Wrobel
# Created: 11/20/15
# Modified: 2/15/15
#-------------------------------------------------------------------------------

from django.views.decorators.csrf import csrf_exempt
from JokrBackend.models import Report as ReportModel 
from JokrBackend.models import OnlineContent
import JokrBackend.Constants as Const
from JokrBackend.Custom import HttpResponseFactory, Utils
from  JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.DataCollection.DataCollector as DataCollector
import JokrBackend.DataCollection.QueryManager as QueryManager

@csrf_exempt
def Report(requestData):
    
    TAG = Const.Tags.Urls.MODERATION_REPORT
    
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
    
    try:
        clientUser = securityProperties.userObject
        clientContentId = securityProperties.jsonRequestData[Const.Views.Report.JsonRequestKey.CONTENT_ID]
        
        # check that the content exists in the database
        clientContent = QueryManager.GetObjectByID(OnlineContent, clientContentId)
        if (not clientContent):
            DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                       responseCode=Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_NOT_FOUND, 
                                       messageCode=Const.DataCollection.MessageCodes.ModerationReport.CONTENT_NOT_FOUND)  
            
            return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_NOT_FOUND, 
                                                        Const.DataCollection.MessageCodes.ModerationReport.CONTENT_NOT_FOUND)
        
        # get the content type that the user is reporting
        contentType = clientContent.contentType
        
        # check if this user has already tried to create this report
        userDupeReports = ReportModel.objects.filter(fromUser=clientUser,
                                                contentID=clientContentId)
        
        # If so, log the hit and return an error to client
        if (userDupeReports):
            DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                       responseCode=Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_CONFLICT, 
                                       messageCode=Const.DataCollection.MessageCodes.ModerationReport.REPORT_EXISTS) 
             
            return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_CONFLICT, 
                                                        Const.DataCollection.MessageCodes.ModerationReport.REPORT_EXISTS) 
        
        # Create the report
        ReportModel.objects.create(fromUser=clientUser,
                                   contentID=Utils.UUIDToBinary(clientContentId),
                                   contentType=contentType)  
        
        # Log the hit and return
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                   responseCode=Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                   messageCode=Const.DataCollection.MessageCodes.ModerationReport.REQUEST_SUCCESSFUL) 
        
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK,
                                                    Const.DataCollection.MessageCodes.ModerationReport.REQUEST_SUCCESSFUL)    
                
    except Exception as e:
        # log and return on error
        DataCollector.logServerError(e)
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID,
                                    responseCode=Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                    messageCode=Const.DataCollection.MessageCodes.ModerationReport.REQUEST_FAILED_SERVER_ERROR) 
        
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.ModerationReport.REQUEST_FAILED_SERVER_ERROR)

    