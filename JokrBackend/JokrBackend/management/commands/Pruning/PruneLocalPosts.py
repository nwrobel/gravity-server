#===============================================================================
# Command that removes all localposts from the database that are older than 
# 'x' minutes. This is to be executed from an external script, which
# is run in the cron at a specified interval.
#
# Nick Wrobel
# Created: 7/3/15
# Modified: 11/6/15 
#===============================================================================

from JokrBackend.models import LocalPost
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
        TAG = Const.Tags.Events.PRUNE_LOCALPOSTS
        
        try:      
            # Only run the pruning if the setting is set
            if(settings.PRUNE_OLD_LOCALPOSTS):  
                                   
                currentTime = time.time()
                oldestTimeAllowed = currentTime - (Const.Pruning.LOCALPOST_MAX_AGE_HOURS * Const.SECONDS_IN_HOUR) 
                numPostsDeleted = 0
                
                # Get all localposts where timeCreated < oldestTimeAllowed
                localPostsToDelete = LocalPost.objects.filter(timeCreated__lt=oldestTimeAllowed)
                
                # remove static content if enabled
                if (settings.PRUNE_STATIC_CONTENT):
                    localPostUrls = []
                    for lp in localPostsToDelete:
                        localPostUrls.append(lp.url)
                        
                    StaticContentUtils.DeleteStaticContent(localPostUrls, 'local')
                           
                # Remove each local post
                for lp in localPostsToDelete:
                    lp.delete()
                    numPostsDeleted += 1
                
            # log info on success 
            DataCollector.logServerEvent(TAG, {
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.Events.PruneLocalPosts.SUCCESS,
                Const.DataCollection.ParamNames.NUM_RECEIVED: len(list(localPostsToDelete)),
                Const.DataCollection.ParamNames.NUM_DELETED: numPostsDeleted  })
            
        except Exception as e:
            # log error and info on error
            DataCollector.logServerError(e)
            DataCollector.logServerEvent(TAG, {
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.Events.PruneLocalPosts.SERVER_ERROR,
                Const.DataCollection.ParamNames.NUM_RECEIVED: len(list(localPostsToDelete)),
                Const.DataCollection.ParamNames.NUM_DELETED: numPostsDeleted  })
            
        
        
        
            