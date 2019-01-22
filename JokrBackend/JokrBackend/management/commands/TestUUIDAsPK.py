#-------------------------------------------------------------------------------
# Command to prune expired session tokens
# 
# Nick Wrobel
# Created: 1/5/16
# Modified: 1/5/16
#-------------------------------------------------------------------------------

from django.core.management import BaseCommand
import time
from JokrBackend.models import User

# Create a class Command to use django manage command functionality
class Command(BaseCommand):
    
    # A command must define handle(), all work happens here
    def handle(self, *args, **options):     
        
        startTime = time.time()

        for x in range(0, 10000):
            User.objects.create()
             
        print('ELAPSED: ', time.time() - startTime, ' seconds')