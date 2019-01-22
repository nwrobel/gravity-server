#-------------------------------------------------------------------------------
# Command to prune expired session tokens
# 
# Nick Wrobel
# Created: 1/5/16
# Modified: 1/5/16
#-------------------------------------------------------------------------------

from JokrBackend.models import SessionToken
from django.core.management import BaseCommand
from django.conf import settings
import time
import JokrBackend.Constants as Const
import JokrBackend.DataCollection.DataCollector as DataCollector

# Create a class Command to use django manage command functionality
class Command(BaseCommand):
    
    # A command must define handle(), all work happens here
    def handle(self, *args, **options):     
        TAG = Const.Tags.Events.PRUNE_SESSION_TOKENS
        
        try: 
            currentTime = time.time()    
            
            # Get all tokens where current time is greater than the time expires 
            expiredTokens = SessionToken.objects.filter(timeExpires__lte=currentTime)
            
            for expiredToken in expiredTokens:
                expiredToken.delete()
                
            # log info on success 
            DataCollector.logServerEvent(TAG, {
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.Events.PruneLocalPosts.SUCCESS,
                Const.DataCollection.ParamNames.NUM_DELETED: len(list(expiredTokens)) })
            
        except Exception as e:
            # log error and info on error
            DataCollector.logServerError(e)
            DataCollector.logServerEvent(TAG, {
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.Events.PruneLocalPosts.SERVER_ERROR,
                Const.DataCollection.ParamNames.NUM_DELETED: 0 })
            
            