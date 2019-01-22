#-------------------------------------------------------------------------------
# ModSearchUser
# Given a user, searches and returns content posted by that user.
# Useful when determining if a user is up to no good.
# 
# Nick Wrobel
# Created: 12/5/15
# Modified: 2/16/15
#-------------------------------------------------------------------------------
import sys
import time
from django.core.management import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from JokrBackend.models import User, OnlineContent, ArchivedContent, Ban, Report, Block
import JokrBackend.Custom.Utils as Utils
import JokrBackend.Constants as Const
from prettytable import PrettyTable
import JokrBackend.DataCollection.QueryManager as QueryManager


class Command(BaseCommand):   
#-------------------------------------------------------------------------------
# __init__
# Set up instance variables 
#-------------------------------------------------------------------------------
    def __init__(self):
        # args
        self.userID = ''
        self.userObject = None
        self.scriptAction = Const.Scripts.Moderation.ArgNames.MODUSER_ACTION_DISPLAY

#-------------------------------------------------------------------------------
# add_arguments
# To set up command line args 
#------------------------------------------------------------------------------- 
    # set up command line args         
    def add_arguments(self, parser):
        parser.add_argument('uuid', nargs=1)        
        parser.add_argument('--action', 
                            default=Const.Scripts.Moderation.ArgNames.MODUSER_ACTION_DISPLAY, 
                            choices=[Const.Scripts.Moderation.ArgNames.MODUSER_ACTION_DISPLAY, 
                                     Const.Scripts.Moderation.ArgNames.MODUSER_ACTION_BAN,
                                     Const.Scripts.Moderation.ArgNames.MODUSER_ACTION_SEARCH],
                            required=False)

#-------------------------------------------------------------------------------
# handle
# Main method for the script  
#------------------------------------------------------------------------------- 
    # A command must define handle(), all work happens here
    def handle(self, *args, **options): 
        
        self.userID = options['uuid'][0]
        self.scriptAction = options['action']
        
        # Get the user object
        self.user = QueryManager.GetObject(User, id=self.userID)
        
        # Exit if not found
        if (not self.user):
            print('User not found with that UUID. Exiting...')
            sys.exit(0)
        
        # Take appropriate action
        if (self.scriptAction == Const.Scripts.Moderation.ArgNames.MODUSER_ACTION_DISPLAY):
            self._DisplayUser()
        elif (self.scriptAction == Const.Scripts.Moderation.ArgNames.MODUSER_ACTION_BAN):
            self._BanUser()
        elif (self.scriptAction == Const.Scripts.Moderation.ArgNames.MODUSER_ACTION_SEARCH):
            self._SearchUser()
                        
#-------------------------------------------------------------------------------
# _DisplayUser
# Displays the info about the user
#-------------------------------------------------------------------------------
    def _DisplayUser(self):
        
        currentTime = time.time()
        
        Utils.PrintStartLine()
        
        # Get basic user info
        print('USER ', self.userID, 'details')
        print('TimeCreated: ', Utils.GetPrettyFormatTimestamp(self.user.timeCreated))
        print('TimeLastUsed: ', Utils.GetPrettyFormatTimestamp(self.user.timeLastUsed))
        
        # Look up how many people have blocked this user on local
        userLocalBlocks = Block.objects.filter(blockedUser=self.user).count()
        print(userLocalBlocks, 'users have blocked this user on local')
        
        # Look up and print all user bans for this user
        userBans = Ban.objects.filter(bannedUser=self.user)
        if (userBans):
            print('Global user bans found:')
            
            for index, ban in enumerate(userBans): # gets the index and the iterator value 
                
                # Check if the ban is current
                banIsCurrent = False
                if (ban.timeExpires > currentTime):
                    banIsCurrent = True
                
                # output info for each ban
                print('Ban ', (index + 1), ':')
                print('    Issued on: ', Utils.GetPrettyFormatTimestamp(ban.timeCreated))
                print('    Duration (hours): ', ban.banLengthHours) 
                print('    Expires: ', Utils.GetPrettyFormatTimestamp(ban.timeCreated + (ban.banLengthHours * Const.SECONDS_IN_HOUR)))
                if (banIsCurrent): 
                    print('    THIS BAN IS CURRENTLY IN EFFECT')
                    
        else:          
            print('No global bans found (past or current) for this user')
            
        Utils.PrintEndLine()
        
#-------------------------------------------------------------------------------
# _BanUser
# Walks the moderator through banning the user.
#-------------------------------------------------------------------------------
    def _BanUser(self):
        
        Utils.PrintStartLine()
        print('Creating a new user ban...')
        print('Enter the ban length in hours (whole numbers only): ')
        
        # Take the ban length. No partial hours, only whole numbers
        banLength = input()
        
        # Check that ban length is good
        if (Utils.IsPositiveInt(banLength)):
                    
            # Check if this user is currently banned . If so, then exit
            if (QueryManager.UserIsBanned(self.user)):
                print('This user is currently under a ban already. Please run\
                 this script on the user to verify')
                sys.exit(0)
                
            # Otherwise, confirm and create the ban
            else:
                print('Are you sure you want to ban user ', self.userID,\
                      ' for ', banLength, ' hours? (y/n)')
                response = input()
                
                if (response == 'Y' or response == 'y'):
                    Ban.objects.create(bannedUser=self.user,
                                       timeBanExpires=int(banLength) * Const.SECONDS_IN_HOUR)
                
                    print('Ban created successfully.  Please run this script on\
                        the user to verify')
                
                else:
                    print('Okay, exiting now')
        
        else:
            print('Ban length must be a positive int. Exiting.')
            sys.exit(0)
            
        Utils.PrintEndLine()
            
#-------------------------------------------------------------------------------
# _SearchUser
# Prints out all content posted by the user in a table format.
#-------------------------------------------------------------------------------
    def _SearchUser(self):
        
        Utils.PrintStartLine()
        print('ALL CONTENT FOR USER ' , self.userID)

        # Get all content posted by this user (archived and online)
        onlineContent = OnlineContent.objects.filter(fromUser=self.user)
        archivedContent = ArchivedContent.objects.filter(fromUser=self.user)
        
        
        table = PrettyTable(['CID', 'Type', 'TimeCreated', 'NumReports', 'ModAction' , 'Online'])
        
        for content in onlineContent:
            numReports = Report.objects.filter(contentID=).count()

        table.add_row([content.id, content.contentType, content.timeCreated, 
                       numReports, modActionType, True])

        
        for contentID in allContentIDs:
            online = False
            archived = False
            
            # If the content is online, get the content from live db
            if (Utils.ContentIsOnline(contentID)):
                content = PostableContent.objects.get(pk=contentID)
                online = True
                
                # If the content is also archived, set the archived flag
                if (Utils.ContentIsArchived(contentID)):
                    archived = True
            
            # Otherwise, get the content from the archive db
            else:
                content = ArchivedPostableContent.objects.get(pk=contentID)
                archived = True

            contentType = content.contentType
            timeCreated = Utils.GetPrettyFormatTimestamp(content.timeCreated)
            
            # Get the number of reports
            numReports = Report.objects.filter(cid=contentID).count()
            modActionType = Utils.GetMostRecentModActionResult(contentID)
            

        
        print(table)
        Utils.PrintEndLine()

#-------------------------------------------------------------------------------
# signal_handler
# interrupt handler, handles the ^C event to stop program
#-------------------------------------------------------------------------------
def signal_handler(signal, frame):
    print ('Exiting ModTop')
    sys.exit(0)
           
        
        
    
        
            

                    
        
        
                
    