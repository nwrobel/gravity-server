#===============================================================================
# Command that removes all local messages from the database that are older than 
# 'x' minutes. This is to be executed within PruneLocalMessagesScript, which
# is run in the cron at a specified interval.
#
# Nick Wrobel
# Created: 7/18/15
# Modified: 11/6/15 
#===============================================================================

from JokrBackend.models import Message
from django.core.management import BaseCommand
from django.conf import settings
import time
import JokrBackend.Constants as Const
import JokrBackend.Custom.StaticContentUtils as StaticContentUtils
import JokrBackend.DataCollection.DataCollector as DataCollector


# Create a class Command to use django manage command functionality
class Command(BaseCommand):
    # A command must define handle(), all work happens here
    def handle(self, *args, **options):
        TAG = Const.Tags.Events.PRUNE_MESSAGES
        
        try:
            if (settings.PRUNE_OLD_MESSAGES):          
                currentTime = time.time()
                oldestTimeAllowed = currentTime - (Const.Pruning.MESSAGE_MAX_AGE_HOURS * Const.SECONDS_IN_HOUR)   
                numMessagesDeleted = 0  
                                
                # Get all messages where timeCreated < oldestTimeAllowed 
                messagesToDelete = Message.objects.filter(timeCreated__lt=oldestTimeAllowed)
                
                # remove static content if enabled
                if (settings.PRUNE_STATIC_CONTENT):
                    messageUrls = []
                    for m in messagesToDelete:
                        messageUrls.append(m.url)
                        
                    StaticContentUtils.DeleteStaticContent(messageUrls, 'message')
                
                # Remove each one
                for m in messagesToDelete:
                    m.delete()
                    numMessagesDeleted += 1
                
            # log info on success 
            DataCollector.logServerEvent(TAG, {
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.Events.PruneLocalPosts.SUCCESS,
                Const.DataCollection.ParamNames.NUM_RECEIVED: len(list(messagesToDelete)),
                Const.DataCollection.ParamNames.NUM_DELETED: numMessagesDeleted  })
            
        except Exception as e:
            # log error and info on error
            DataCollector.logServerError(e)
            DataCollector.logServerEvent(TAG, {
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.Events.PruneLocalPosts.SERVER_ERROR,
                Const.DataCollection.ParamNames.NUM_RECEIVED: len(list(messagesToDelete)),
                Const.DataCollection.ParamNames.NUM_DELETED: numMessagesDeleted  })
            