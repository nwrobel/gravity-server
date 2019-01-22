#===============================================================================
# GetThreadView
# Returns to the client a snapshot of all the threads on a board at a given
# time. Only threads and their metadata is returned, not replies.
#
# Nick Wrobel
# Created: 7/20/15
# Modified: 2/15/16
#===============================================================================

from django.views.decorators.csrf import csrf_exempt
import simplejson as json
import collections
from JokrBackend.models import Thread, Reply
import JokrBackend.Constants as Const
from JokrBackend.Custom import HttpResponseFactory
from JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
import JokrBackend.Custom.Utils as Utils
import JokrBackend.DataCollection.DataCollector as DataCollector
import JokrBackend.DataCollection.QueryManager as QueryManager


@csrf_exempt
def GetLive(requestData):
    TAG = Const.Tags.Urls.GET_LIVE
        
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
    
    try:        
        # Get the list of threads
        jsonString = GetThreadListJsonString()

        # log and return on success          
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID, 
                                   responseCode=Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK,
                                   messageCode=Const.DataCollection.MessageCodes.GetLive.REQUEST_SUCCESSFUL)
                       
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                                    jsonString, 'application/json')
    
    except Exception as e:
        # log and return on error
        DataCollector.logServerError(e)
        DataCollector.UpdateURLHit(hitID=securityProperties.hitID, 
                                   responseCode=Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR,
                                   messageCode=Const.DataCollection.MessageCodes.GetLive.REQUEST_FAILED_SERVER_ERROR)
 
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.GetLive.REQUEST_FAILED_SERVER_ERROR)
        

#-------------------------------------------------------------------------------
# Returns the list of live threads, along with their attributes, in Json form
# This is also used by /live/upload/
#-------------------------------------------------------------------------------
def GetThreadListJsonString():
    
    # get the threads by time created
    threads = QueryManager.GetLiveThreadsByTimeLastActive()
        
    # Get the stuff we need from the thread, package and return to the client
    clientThreadsToReturn = []
    for index, thread in enumerate(threads):
        objectToReturn = _GetThreadClientObject(id=Utils.BinaryToUUID(thread.id),
                                                text=thread.text, 
                                                time=thread.timeCreated, 
                                                key=thread.key,
                                                order=index,
                                                replies=thread.replyCount,
                                                unique=thread.uniquePostersCount,
                                                arn=thread.arn) 
        clientThreadsToReturn.append(objectToReturn.getOrderedDict())   
           
    return json.dumps(clientThreadsToReturn)

#------------------------------------------------------------------------------ 
# This class is a wrapper for the info of a live thread to be sent to client.
#------------------------------------------------------------------------------ 
class _GetThreadClientObject:
    def __init__(self, id, text, time, key, order, replies, unique, arn):
        self.id = id
        self.text = text
        self.time = time
        self.key = key
        self.order = order
        self.replies = replies
        self.unique = unique
        self.arn= arn
        
        # Format the optional fields - if they are null, use empty string
        if Utils.StringIsEmpty(key):
            self.key = ''
        if Utils.StringIsEmpty(text):
            self.text = ''
        
    # Returns an ordered dictionary. This is 
    # necessary in order to properly json stringify the object.
    def getOrderedDict(self):
       
        dict = collections.OrderedDict()
        dict[Const.Views.GetThread.JsonResponseKey.THREAD_ID] = self.id
        dict[Const.Views.GetThread.JsonResponseKey.THREAD_ORDER] = self.order
        dict[Const.Views.GetThread.JsonResponseKey.THREAD_NUM_REPLIES] = self.replies
        dict[Const.Views.GetThread.JsonResponseKey.THREAD_NUM_UNIQUE_POSTERS] = self.unique
        dict[Const.Views.GetThread.JsonResponseKey.THREAD_TEXT] = self.text
        dict[Const.Views.GetThread.JsonResponseKey.THREAD_TIME] = self.time
        dict[Const.Views.GetThread.JsonResponseKey.THREAD_URL] = self.key
        dict[Const.Views.GetThread.JsonResponseKey.THREAD_ARN] = self.arn
        return dict
