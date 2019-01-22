#===============================================================================
# Command that removes all old users from the database.
#
# Nick Wrobel
# Created: 7/29/15
# Modified: 11/2/15 
#===============================================================================

from JokrBackend.models import User
from django.core.management import BaseCommand
from django.conf import settings
import logging
import time
import JokrBackend.Constants as Const

# Set up the logging
logger = logging.getLogger(__name__)


# Create a class Command to use django manage command functionality
class Command(BaseCommand):
    # A command must define handle(), all work happens here
    def handle(self, *args, **options):
              
        if (settings.PRUNE_OLD_USERS):
            
            currentTime = time.time()
            oldestTimeAllowed = currentTime - (Const.Pruning.USER_MAX_AGE_DAYS * Const.SECONDS_IN_DAY) 
            numUsersDeleted = 0
            
            # Get the old users
            usersToDelete = User.objects.filter(timeLastUsed__lt=oldestTimeAllowed)
            
            # Delete the old users
            for u in usersToDelete:
                u.delete()
                numUsersDeleted += 1
            
            logger.info('Pruning run: ' + str(numUsersDeleted) + ' user accounts deleted')
            
