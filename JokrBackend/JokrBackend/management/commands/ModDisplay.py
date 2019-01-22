#-------------------------------------------------------------------------------
# ModDisplay
# Displays more information about a particular piece of content
# 
# Nick Wrobel
# Created: 12/5/15
# Modified: 2/16/15
#-------------------------------------------------------------------------------
import sys
import os
import signal
from django.conf import settings
from django.core.management import BaseCommand
from JokrBackend.models import OnlineContent, ArchivedContent, LocalPost, Message, Thread, Reply, ArchivedLocalPost, ArchivedMessage, ArchivedThread, ArchivedReply, Report, ModAction
import JokrBackend.Constants as Const
import JokrBackend.Custom.Utils as Utils
import JokrBackend.Custom.StaticContentUtils as StaticContentUtils
import JokrBackend.DataCollection.QueryManager as QueryManager
import JokrBackend.DataCollection.ContentManager as ContentManager


class Command(BaseCommand): 

#-------------------------------------------------------------------------------
# __init__
# Set up instance variables 
#-------------------------------------------------------------------------------
    def __init__(self):
        # args
        self.contentID = ''
        self.showImage = False
        self.showModInfo = False
        self.promptForModAction = False
        self.showFullThread = False
        
        # the content object
        self.content = None
        
        # whether or not content is archived
        self.archived = False
        
#-------------------------------------------------------------------------------
# add_arguments
# set up command line args  
#-------------------------------------------------------------------------------    
    def add_arguments(self, parser):
        # positional argument, the content ID
        parser.add_argument('id', nargs=1) 
        
        # optional arguments
        parser.add_argument('--showimage', default=False, required=False)
        parser.add_argument('--modinfo', default=False, required=False)
        parser.add_argument('--moderate', default=False, required=False)
        parser.add_argument('--fullthread', default=False, required=False)

#-------------------------------------------------------------------------------
# handle
# the 'main method'
#-------------------------------------------------------------------------------
    def handle(self, *args, **options): 
        
        # Get the input arguments
        self.contentID = options['id'][0]
        self.showImage = options['showimage']
        self.showModInfo = options['modinfo']
        self.promptForModAction = options['moderate']
        self.showFullThread = options['fullthread']
        
        # set up interrupt hander for ctrl+c event
        signal.signal(signal.SIGINT, signal_handler)
        
        self._GetContent()     
        self._PrintContent()
         
        # Open the image if we need to 
        # Open the image by default if the user has selected to moderate              
        if (self.showImage or self.promptForModAction):
            self._DownloadAndOpenImage()
        
        # Allow a mod to do something, if we need to  
        if (self.promptForModAction):
            self._PromptForModAction()
            
#-------------------------------------------------------------------------------
# _GetContent
# Gets the content, checking both online and archive, and outputs the results.
#-------------------------------------------------------------------------------
    def _GetContent(self):
        
        # check online and archive tables
        if (QueryManager.ContentIsOnline(self.contentID)):
            self.content = OnlineContent.objects.get(id=self.contentID)
        elif (QueryManager.ContentIsArchived(self.contentID)):
            self.content = ArchivedContent.objects.get(id=self.contentID)
            self.archived = True
        else:
            print('Content does not exist in online or archive tables')
            sys.exit(0)   
        
        # Display a warning note to user about archived content
        if (self.archived):            
            print('Note: Specified content is archived (not online). Therefore\
                    content can only be displayed (no moderation actions can be\
                    taken)')
      
#-------------------------------------------------------------------------------
# Prints out the specified content, given the content object and some options
# 
# Params:
#    content - the content object
#    onlyArchived - if the content only exists in the archive or not
#    showModInfo/showFullThread - command line options 
#-------------------------------------------------------------------------------
    def _PrintContent(self):
    
        contentType = self.content.contentType
        
        # Localpost
        if (contentType == Const.Tags.ContentTypes.LOCALPOST):
            self._PrintLocalPost()
        
        # Message
        if (contentType == Const.Tags.ContentTypes.MESSAGE):
            self._PrintMessage()
    
            
        # Thread
        if (contentType == Const.Tags.ContentTypes.THREAD):
            self._PrintThread()
    
        
        # Reply
        if (contentType == Const.Tags.ContentTypes.REPLY):
            self._PrintReply()
 
#-------------------------------------------------------------------------------
# _PrintLocalPost
#-------------------------------------------------------------------------------
    def _PrintLocalPost(self):
        if (self.archived):
            lp = QueryManager.GetObjectByID(ArchivedLocalPost, self.contentID)
        else:
            lp = QueryManager.GetObjectByID(LocalPost, self.contentID)
        
        Utils.PrintStartLine()
        print('LOCALPOST (CID ', self.contentID, ')')
        print('TimeCreated: ', Utils.GetPrettyFormatTimestamp(self.content.timeCreated))
        print('FromUser: ', self.content.fromUser.id)
        print('GPS: (', lp.latitude, ' , ', lp.longitude, ')')
        print('Text: ', lp.text)
        
        # Gather and print the mod info if the setting is set
        if (self.showModInfo):
            self._PrintModInfo(self.contentID)
        Utils.PrintEndLine()
    
#-------------------------------------------------------------------------------
# _PrintMessage
#-------------------------------------------------------------------------------
    def _PrintMessage(self):
        if (self.archived):
            ms = QueryManager.GetObjectByID(ArchivedMessage, self.contentID)
        else:
            ms = QueryManager.GetObjectByID(Message, self.contentID)
            
        Utils.PrintStartLine()
        print('MESSAGE (CID ', self.contentID, ')')
        print('TimeCreated: ', Utils.GetPrettyFormatTimestamp(self.content.timeCreated))
        print('FromUser: ', self.content.fromUser.id)
        print('ToUser: ', self.content.toUser.id)
        print('Text: ', ms.text)

        # Gather and print the mod info if the setting is set
        if (self.showModInfo):
            self._PrintModInfo(self.contentID)
        Utils.PrintEndLine()
        
#-------------------------------------------------------------------------------
# _PrintThread
#-------------------------------------------------------------------------------
    def _PrintThread(self):
        if (self.archived):
            th = QueryManager.GetObjectByID(ArchivedThread, self.contentID)
        else:
            th = QueryManager.GetObjectByID(Thread, self.contentID)

        Utils.PrintStartLine()
        print('THREAD (CID ', self.contentID, ')')
        print('TimeCreated: ', Utils.GetPrettyFormatTimestamp(self.content.timeCreated))
        print('FromUser: ', self.content.fromUser.id)
        print('Title: ', th.title)
        print('OpName: ', th.name)
        print('NumReplies: ', th.replyCount)
        print('Text: ', th.text)
         
        # Gather and print the mod info if the setting is set
        if (self.showModInfo):
            self._PrintModInfo(self.contentID)
        Utils.PrintEndLine()   
  
        if (self.showFullThread):
            self._PrintThreadReplies(self.contentID)
    
#-------------------------------------------------------------------------------
# _PrintReply
#-------------------------------------------------------------------------------
    def _PrintReply(self):
        if (self.archived):
            re = QueryManager.GetObjectByID(ArchivedReply, self.contentID)
        else:
            re = QueryManager.GetObjectByID(Reply, self.contentID)
        
        Utils.PrintStartLine()
        print('REPLY (CID ', self.contentID, ')')
        print('TimeCreated: ', Utils.GetPrettyFormatTimestamp(self.content.timeCreated))
        print('FromUser: ', self.content.fromUser.id)
        print('OpName: ', re.name)
        print('HasImage: ', bool(re.url))
        print('Text: ', re.text)
         
        # Gather and print the mod info if the setting is set
        if (self.showModInfo):
            self._PrintModInfo()
        Utils.PrintEndLine() 

#-------------------------------------------------------------------------------
# _PrintThreadReplies
# Prints out each reply to a thread in the console, omitting the images.
#-------------------------------------------------------------------------------
    def _PrintThreadReplies(self):
        replies = QueryManager.GetThreadReplies(self.contentID)
        
        print('PRINITING REPLIES FOR THEAD (CID ', self.contentID, ')')
        
        for re in replies:
            print('--------------------------------------------------------------------------------') 
            print('REPLY (CID ', Utils.BinaryToUUID(re.cid.id), ')')
            print('TimeCreated: ', Utils.GetPrettyFormatTimestamp(re.timeCreated))
            print('FromUser: ', Utils.BinaryToUUID(re.fromUser.uuid))
            print('OpName: ', re.name)
            print('HasImage: ', bool(re.url))
            print('Text: ', re.text)
            
        Utils.PrintEndLine()
                        
#-------------------------------------------------------------------------------
# _PrintModInfo
# Prints out relevent moderation info for a piece of content
#-------------------------------------------------------------------------------
    def _PrintModInfo(self, contentID):
        numReports = Report.objects.filter(cid=Utils.UUIDToBinary(contentID)).count()
        online = False
        archived = False
        modActionType = ''
        
        if (QueryManager.ContentIsOnline(contentID)):
            online = True
        if (QueryManager.ContentIsArchived(contentID)):
            archived = True
        
        # Get the mod action associated with the piece of content, if there is one
        modActionType = QueryManager.GetMostRecentModActionResult(contentID)
     
        print('NumReports: ', numReports)
        print('Online: ', online)
        print('Archived: ', archived)
        print('Most recent mod action: ', 'N/A' if not modActionType else modActionType) # ternary operator in python ;) 
        
#-------------------------------------------------------------------------------
# _DownloadAndOpenImage
# Downloads an image from S3 into a cache directory and opens the image
# using feh (must be installed on host computer, with X11Forwarding=yes in 
# the ssh config, if using over ssh)
#-------------------------------------------------------------------------------
    def _DownloadAndOpenImage(self, content, onlyArchived):
        print('Downloading S3 image..')
        StaticContentUtils.DownloadStaticContent(key=content.url, 
                                                 getFromArchive=onlyArchived,
                                                 downloadDir=settings.MODERATION_CACHE_DIR)
        openImg = lambda: os.system('feh ' + settings.MODERATION_CACHE_DIR + content.url)
        openImg()
        
#-------------------------------------------------------------------------------
# _PromptForModAction
# Prompts for moderator action and takes the selected action
#-------------------------------------------------------------------------------
    def _PromptForModAction(self):
        
        # Display options
        print('You have viewed this content. Please enter an action:')
        print('del - delete the content')
        print('ok - mark content as not offensive and safe')
        print('pen - mark content as needing further review')
        print('ig - ignore the content (temporary)')
        print('q - quit the program')
        input_var = input() # get input in python
        
        # Delete
        if (input_var == 'del'):
            print('Are you sure you want to delete ', self.content.type,\
                  ' ', self.contentID, '? (y/n)')
            input_var = input()
            
            # mark reports with a modAction 'deleted' and delete the content,
            # if the user confirms
            if (input_var == 'Y' or input_var == 'y'):
                self._ModActionMark(Const.Tags.ModActions.CONTENT_DELETED)
                ContentManager.DeleteContent(self.contentID)
                print('Deletion complete')
            else:
                print('Exiting')
        
        # Okay  
        elif (input_var == 'ok'):
            print('Are you sure you want to mark', self.content.type,\
                  ' ', self.contentID, ' as safe? (y/n)')
            input_var = input()
            
            if (input_var == 'Y' or input_var == 'y'):
                self._ModActionMark(Const.Tags.ModActions.CONTENT_OK)
                print('Successfully marked as safe')
            else:
                print('Exiting')
                
        # Pending
        elif (input_var == 'pen'):
            print('Are you sure you want to mark', self.content.type,\
                  ' ', self.contentID, ' as pending for review? (y/n)')
            input_var = input()
            
            if (input_var == 'Y' or input_var == 'y'):
                self._ModActionMark(Const.Tags.ModActions.REVIEW_PENDING)   
                print('Successfully marked as pending for review')
            else:
                print('Exiting')
                
        # Ignored
        elif (input_var == 'ig'):
            print('Are you sure you want to ignore', self.content.type,\
                  ' ', self.contentID, '? You can come back it later (y/n)')
            input_var = input()
            
            if (input_var == 'Y' or input_var == 'y'):
                self._ModActionMark(Const.Tags.ModActions.REVIEW_PENDING)   
                print('Successfully marked as ignored')
            else:
                print('Exiting')        
      
#-------------------------------------------------------------------------------
# _ModActionMark
# Creates a moderation action and marks all relevant reports with the correct
# moderation code. 
# 
# Params:
#    modActionResultCode - the mod result code { 'OK', 'DEL', 'PEN', 'IGN' }
#-------------------------------------------------------------------------------
    def _ModActionMark(self, modActionResultCode):
        # Create the mod action
        newModAction = ModAction.objects.create(result=modActionResultCode,
                                 cid=Utils.UUIDToBinary(self.contentID),
                                 contentType=self.content.contentType)
        
        # Update all reports
        Report.objects.filter(cid=Utils.UUIDToBinary(self.contentID))\
                                .update(modAction=newModAction)
        
#-------------------------------------------------------------------------------
# signal_handler
# interrupt handler, handles the ^C event to stop program
#-------------------------------------------------------------------------------
def signal_handler(signal, frame):
    print ('Exiting ModDisplay')
    sys.exit(0)
        
                
    