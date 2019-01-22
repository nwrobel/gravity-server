#-------------------------------------------------------------------------------
# ModTop
# This script (which works like the 'top' command in linux) outputs the 
# top pieces of content, ordered by reports.
# 
# Nick Wrobel
# Created: 11/21/15
# Modified: 2/16/15
#-------------------------------------------------------------------------------

import sys
import time
import signal
from prettytable import PrettyTable
from django.core.management import BaseCommand
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from JokrBackend.models import Report, ModAction, OnlineContent, ArchivedContent
import JokrBackend.Constants as Const
import JokrBackend.Custom.Utils as Utils
import JokrBackend.DataCollection.QueryManager as QueryManager


class Command(BaseCommand):    
#-------------------------------------------------------------------------------
# __init__
# Set up instance variables 
#-------------------------------------------------------------------------------
    def __init__(self):
        # args
        self.refreshRate = 2
        self.filterByType = 'all'
        self.excludeOffline = False
        
#-------------------------------------------------------------------------------
# add_arguments
# To set up command line args 
#-------------------------------------------------------------------------------     
    def add_arguments(self, parser):
        parser.add_argument('--rate', default=2, required=False)
        parser.add_argument('--type', default='all', 
                            choices=[Const.Tags.ContentTypes.LOCALPOST,
                                     Const.Tags.ContentTypes.MESSAGE,
                                     Const.Tags.ContentTypes.THREAD,
                                     Const.Tags.ContentTypes.REPLY],
                            required=False)
        parser.add_argument('--excludeoffline', default=False, required=False)
        
#-------------------------------------------------------------------------------
# handle
# Main method for the script  
#------------------------------------------------------------------------------- 
    def handle(self, *args, **options): 
        
        # get the params from the command line
        self.refreshRate = options['rate']
        self.filterByType = options['type']
        self.excludeOffline = options['excludeoffline']
        
        # set up interrupt handler for ctrl+C exit event
        signal.signal(signal.SIGINT, signal_handler)
        
        Utils.ClearConsole()
        
        # Constantly refresh
        while (True):  
            # Create a new table for the results each time  
            table = None 
            table = PrettyTable(['CID', 'Type', 'TimeCreated', 'FromUser', 'NumReports', 'ModAction' , 'Online'])
            
            # Get the list of reports
            reports = self._GetReports()
            
            # For each report group, gather the data to be displayed
            # and add it to the table if there is any data returned
            for report in reports:
                data = self._GetTableDataForReport(report)
                if (data):
                    table.add_row(data)
            
            # Print the results and pause for the refreshRate      
            print (table)
            time.sleep(float(self.refreshRate))
            Utils.ClearConsole()
            print('Updating results every ', self.refreshRate, ' seconds')

#-------------------------------------------------------------------------------
# _GetReports
# Gets the list of reports, grouped by a common reported content.
# 
# Returns:
#    list of reports, each element having 'cid', 'modAction_id', 'contentType'
#-------------------------------------------------------------------------------
    def _GetReports(self):
        
        # Filter by content type, if needed
        if (self.filterByType == Const.Tags.ContentTypes.LOCALPOST):
            reports = Report.objects.filter(contentType=Const.Tags.ContentTypes.LOCALPOST)
            
        elif (self.filterByType == Const.Tags.ContentTypes.MESSAGE):
            reports = Report.objects.filter(contentType=Const.Tags.ContentTypes.MESSAGE)
            
        elif (self.filterByType == Const.Tags.ContentTypes.THREAD):
            reports = Report.objects.filter(contentType=Const.Tags.ContentTypes.THREAD)
            
        elif (self.filterByType == Const.Tags.ContentTypes.REPLY):
            reports = Report.objects.filter(contentType=Const.Tags.ContentTypes.REPLY)
            
        else:
            reports = Report.objects.all()
            
        # Get cid, modAction_id, and contentType values from reports table
        # Group results (collapse) by their CID and call the number of 
        # reports in each group 'num_reports'
        # Each 'report' is actually multiple reports, grouped by a common content 
        reports = reports.values('contentID', 'modAction_id', 'contentType')\
                            .annotate(num_reports=Count('contentID'))\
                            .order_by('-num_reports')
        return reports

#-------------------------------------------------------------------------------
# _GetTableDataForReport
# Gets the data for a row in the ModTop table, given a report group item.
# 
# Params:
#    report - the report item 
# Returns:
#    a list of table data
#    [cid, contentType, timeCreated, fromUser, numReports, modActionType, online]
#-------------------------------------------------------------------------------
    def _GetTableDataForReport(self, report):
        
        # Init data
        cid = Utils.StipUUIDDashes(report['contentID'])
        modActionID = report['modAction_id']  
        numReports = report['num_reports']
        contentType = report['contentType']
        timeCreated = ''
        fromUser = ''
        modActionType = ''
        online = False
    
        # Get the mod action from this report group if it exists                 
        try:
            modActionType = ModAction.objects.get(pk=modActionID).result
        except ObjectDoesNotExist:
            pass
        
        # Try to lookup the content from the online table
        onlineContent = QueryManager.GetObject(OnlineContent, id=cid)
        
        # If it is there, then use the info from it
        if (onlineContent):
            online = True
            contentType = onlineContent.contentType
            timeCreated = Utils.GetPrettyFormatTimestamp(onlineContent.timeCreated)
            fromUser = onlineContent.fromUser.id
            return [cid, contentType, timeCreated, fromUser, numReports, modActionType, online]
                
        # if the content is not online, then check the archives
        # (Only if the --excludeoffline flag is not set)       
        elif (not self.excludeOffline):                    
    
            # Try to get the archived content
            archivedContent = QueryManager.GetObject(ArchivedContent, pk=cid)
            
            if (archivedContent):
                contentType = archivedContent.contentType
                timeCreated = Utils.GetPrettyFormatTimestamp(archivedContent.timeCreated)
                fromUser = archivedContent.fromUser.id
                return [cid, contentType, timeCreated, fromUser, numReports, modActionType, online]

#-------------------------------------------------------------------------------
# signal_handler
# interrupt handler, handles the ^C event to stop program
#-------------------------------------------------------------------------------
def signal_handler(signal, frame):
    print ('Exiting ModTop')
    sys.exit(0)
            
            

    
            
    