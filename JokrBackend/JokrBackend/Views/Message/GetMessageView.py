#===============================================================================
# GetMessageView
# View that lets a client check if he has any unread messages on the local feed.
#
# Nick Wrobel
# Created: 7/9/15
# Modified: 11/6/15
#===============================================================================

from django.views.decorators.csrf import csrf_exempt
import simplejson as json
from JokrBackend.models import Message
from JokrBackend.Custom.Utils import ConvertBinaryToUUID
import JokrBackend.Constants as Const
from JokrBackend.Custom import HttpResponseFactory
from  JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.Custom.Utils as Utils
import JokrBackend.DataCollection.DataCollector as DataCollector

@csrf_exempt
def GetMessage(requestData):
    TAG = Const.Tags.Urls.GET_MESSAGE
        
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
    
    try:
        
        clientUser = securityProperties.clientUserObject
        
        # Retrieve all this user's messages from the DB
        messages = Message.objects.filter(toUser=clientUser)
        clientMessageListToReturn = []
        for lm in messages:
            clientMessageToReturn = _GetMessageClientObject(id=lm.id,
                                                            time=lm.timeCreated, 
                                                            fromUserId=str(ConvertBinaryToUUID(lm.fromUser.uuid)),
                                                            text=lm.text,
                                                            url=lm.url)
            clientMessageListToReturn.append(clientMessageToReturn.getOrderedDict())
            
        jsonString = json.dumps(clientMessageListToReturn)
        
    
        # Delete all this user's messages from the DB, since we are about to give
        # them their messages (this is temporary)
        for m in messages:
            m.delete()

        # log and return on success  
        DataCollector.logURL(TAG, { 
            Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK,
            Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.GetMessage.REQUEST_SUCCESSFUL,
            Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid),
            Const.DataCollection.ParamNames.NUM_MESSAGES_RECEIVED: len(list(messages))  })
    
                 
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                jsonString, 'application/json')
        
    except Exception as e:
        DataCollector.logServerError(e)
        DataCollector.logURL(TAG, { 
            Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR,
            Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.GetMessage.REQUEST_FAILED_SERVER_ERROR,
            Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid),
            Const.DataCollection.ParamNames.NUM_MESSAGES_RECEIVED: len(list(messages))  })        
        
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.GetMessage.REQUEST_FAILED_SERVER_ERROR)
        
        
        
#------------------------------------------------------------------------------ 
# This class is a wrapper for a Local message to be sent to the client. 
#------------------------------------------------------------------------------ 
class _GetMessageClientObject:
    def __init__(self, id, time, fromUserId, text, url):
        self.id = id
        self.time = time
        self.fromUserId = fromUserId
        self.text = text
        self.url = url

    # Returns an ordered dictionary of the LocalPostObject content. This is 
    # necessary in order to properly json stringify the object.
    def getOrderedDict(self):
        import collections
        
        dict = collections.OrderedDict()
        dict[Const.Views.GetMessage.JsonResponseKey.MESSAGE_ID] = self.id
        dict[Const.Views.GetMessage.JsonResponseKey.MESSAGE_TIME] = self.time
        dict[Const.Views.GetMessage.JsonResponseKey.SENDER_USER_ID] = self.fromUserId
        dict[Const.Views.GetMessage.JsonResponseKey.MESSAGE_TEXT] = self.text
        dict[Const.Views.GetMessage.JsonResponseKey.MESSAGE_URL] = self.url
        return dict
            


    