#===============================================================================
# UploadMessageView
# View that lets a client send a message to another user on the local feed.
#
# Nick Wrobel
# Created: 7/9/15
# Modified: 11/6/15
#===============================================================================

from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from JokrBackend.models import User, Message
import JokrBackend.Custom.Utils as Utils
import JokrBackend.Constants as Const
from JokrBackend.Custom import HttpResponseFactory
from  JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.DataCollection.DataCollector as DataCollector


@csrf_exempt
def UploadMessage(requestData):
    TAG = Const.Tags.Urls.UPLOAD_MESSAGE
         
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
    
    try:
        clientUser = securityProperties.clientUserObject
        clientRecipientUserUUID = securityProperties.jsonRequestData[Const.Views.UploadMessage.JsonRequestKey.TO_USER_ID]
        clientMessageText = securityProperties.jsonRequestData[Const.Views.UploadMessage.JsonRequestKey.TEXT]
        clientMessageURL = securityProperties.jsonRequestData[Const.Views.UploadMessage.JsonRequestKey.URL]

        # Find the recipient user in the DB
        try:
            recipientUser = User.objects.get(uuid=Utils.ConvertUUIDToBinary(clientRecipientUserUUID))
        except ObjectDoesNotExist:
            DataCollector.logURL(TAG, { 
                Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_UNPROCESSABLE_ENTITY,
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.UploadMessage.RECIPIENT_NOT_FOUND,
                Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid),
                Const.DataCollection.ParamNames.TO_USER: Utils.ConvertBinaryToUUID(recipientUser.uuid),
                Const.DataCollection.ParamNames.HAS_TEXT: (not Utils.StringIsEmpty(clientMessageText)) }) 
                        
            return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ClientError.CODE_UNPROCESSABLE_ENTITY, 
                                                        Const.DataCollection.MessageCodes.UploadMessage.RECIPIENT_NOT_FOUND)
    

        # Save the message in the DB
        newMessage = Message(toUser=recipientUser,
                             fromUser=clientUser,
                             text=clientMessageText,
                             url=clientMessageURL,
                             contentType=Const.Tags.ContentTypes.MESSAGE)
    
        # If there is an exception, roll back this db transaction
        with transaction.atomic():
            newMessage.save()

        # log and return on success
        DataCollector.logURL(TAG, { 
            Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK,
            Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.UploadMessage.POST_SUCCESSFUL,
            Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid),
            Const.DataCollection.ParamNames.TO_USER: Utils.ConvertBinaryToUUID(recipientUser.uuid),
            Const.DataCollection.ParamNames.HAS_TEXT: (not Utils.StringIsEmpty(clientMessageText)) })  
    
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                                Const.DataCollection.MessageCodes.UploadMessage.POST_SUCCESSFUL)
        
            
    except Exception as e:
        DataCollector.logServerError(e)
        DataCollector.logURL(TAG, { 
            Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR,
            Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.UploadMessage.POST_FAILED_SERVER_ERROR,
            Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid),
            Const.DataCollection.ParamNames.TO_USER: Utils.ConvertBinaryToUUID(recipientUser.uuid),
            Const.DataCollection.ParamNames.HAS_TEXT: (not Utils.StringIsEmpty(clientMessageText)) }) 

        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.UploadMessage.POST_FAILED_SERVER_ERROR)

    