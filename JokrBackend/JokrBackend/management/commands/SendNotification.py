#------------------------------------------------------------------------------ 
# Command to fetch and display the most recent server exceptions from python 
# code from the database.
#
# Nick Wrobel
# Created: 1/4/16
# Modified: 1/4/16 
#------------------------------------------------------------------------------ 
from JokrBackend.models import Error
from django.core.management import BaseCommand
import JokrBackend.Custom.Utils as Utils

# Create a class Command to use django manage command functionality
class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('text', nargs=1) 
         
    # A command must define handle(), all work happens here
    def handle(self, *args, **options): 
        text = options['text']