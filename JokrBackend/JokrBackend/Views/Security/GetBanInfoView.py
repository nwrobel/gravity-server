#===============================================================================
# Ban info view
# Allows a user to check their app-wide ban status
#
# Nick Wrobel
# Created: 12/16/15
# Modified: 12/16/15
#===============================================================================

from django.views.decorators.csrf import csrf_exempt
import simplejson as json
import time
from JokrBackend.models import Ban
import JokrBackend.Constants as Const
from JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 
from JokrBackend.Custom import HttpResponseFactory
import JokrBackend.Custom.Utils as Utils
import JokrBackend.DataCollection.DataCollector as DataCollector

        
@csrf_exempt
def GetBanInfo(requestData):
    TAG = Const.Tags.Urls.SECURITY_GETBANINFO
    
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    if (not securityProperties.isSecure):
        return securityProperties.httpResponse
       
    try:
        clientUser = securityProperties.clientUserObject
        banLength = ''
        banTimeCreated = ''

        # Check if the user has any bans
        userBan = Ban.objects.filter(bannedUser=clientUser).order_by('-timeCreated')[:1]
    
        # If there is a ban, check to make sure it is still active
        if(userBan):
            userBan = userBan[0]
            banExpires = userBan.timeCreated + (userBan.banLengthHours * Const.SECONDS_IN_HOUR)
        
            # If the ban expir. time is past the current time, then the user is 
            # still currently under a ban
            if (banExpires > time.time()):
                banTimeCreated = userBan.timeCreated
                banLength = userBan.banLengthHours
        
        clientObject = _BanInfoClientObject(banStartTime=banTimeCreated,
                                        banEndTime=(banTimeCreated + (banLength * Const.SECONDS_IN_HOUR)))
        jsonString = json.dumps(clientObject.getOrderedDict())


        DataCollector.logURL(TAG, { 
            Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK,
            Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.SecurityGetBanInfo.REQUEST_SUCCESSFUL,
            Const.DataCollection.ParamNames.FROM_USER: Utils.ConvertBinaryToUUID(clientUser.uuid) })
              
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.Success.CODE_OK, 
                                                    jsonString, 'application/json')
        
    except Exception as e:
        DataCollector.logServerError(e)
        DataCollector.logURL(TAG, {
            Const.DataCollection.ParamNames.RESPONSE_CODE: Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR,
            Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.SecurityGetBanInfo.REQUEST_FAILED_SERVER_ERROR,
            Const.DataCollection.ParamNames.NEW_USER: ''})
        
        return HttpResponseFactory.MakeHttpResponse(Const.HttpResponseFactory.ResponseCodes.ServerError.CODE_INTERNAL_SERVER_ERROR, 
                                                    Const.DataCollection.MessageCodes.SecurityGetBanInfo.REQUEST_FAILED_SERVER_ERROR)
        
        
    
#------------------------------------------------------------------------------ 
# This class is a wrapper for the json of initialize user to be sent to client.
#------------------------------------------------------------------------------ 
class _BanInfoClientObject:
    def __init__(self, banStartTime, banEndTime):
        self.banStartTime = banStartTime
        self.banEndTime = banEndTime
        
    # Returns an ordered dictionary. This is 
    # necessary in order to properly json stringify the object.
    def getOrderedDict(self):
        import collections

        dict = collections.OrderedDict()
        dict[Const.Views.GetBanInfo.JsonResponseKey.BAN_TIME_CREATED] = self.banStartTime
        dict[Const.Views.GetBanInfo.JsonResponseKey.BAN_TIME_EXPIRES] = self.banEndTime        
        return dict
    
    
