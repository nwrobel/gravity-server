#-------------------------------------------------------------------------------
# Data collector module
# Serves as the logging module for the server.
# 
# Nick Wrobel
# Created: 11/4/15
# Modified: 1/4/16
#-------------------------------------------------------------------------------

import logging
import io
from contextlib import redirect_stdout
from django.db.models.query import QuerySet
from JokrBackend.models import *
from django.core.exceptions import ObjectDoesNotExist
import JokrBackend.DataCollection.Notifier as Notifier
# from JokrBackend.models.Content import OnlineContent, ArchivedContent
# from JokrBackend.models.Moderation import Ban, ModAction

#-------------------------------------------------------------------------------
# LogURLHitRequest
# Logs a URL hit, given the security properties object
# This returns a hitID, so we can track this hit and add a status and 
# message code to it later when it passes through a view.
#-------------------------------------------------------------------------------
def LogURLHit(securityProperties):
    
    # If there is a security error, log the hit and the error at the same time
    # The response code and message code are known already and are set
    if (not securityProperties.isSecure):
        hit = SecurityErrorHit.objects.create(
                        url=securityProperties.requestedURL,
                        responseCode=securityProperties.httpResponse.status_code,
                        messageCode=Const.DataCollection.MessageCodes.Security.ERROR,
                        ip=securityProperties.clientIP,
                        fromUser=securityProperties.userObject,
                        session=securityProperties.userSession,
                        requestMethod=securityProperties.requestMethod,
                        requestContentType=securityProperties.requestContentType,
                        requestData=securityProperties.requestData,
                        errors=Utils.ListToCSV(securityProperties.errorsList))
    
    # Otherwise, simply log the hit, and we can come back to the response code
    # and message code later    
    else:    
        hit = Hit.objects.create(
                        url=securityProperties.requestedURL,
                        ip=securityProperties.clientIP,
                        fromUser=securityProperties.userObject,
                        session=securityProperties.userSession)
    
    # return the hitID
    return hit.id

#-------------------------------------------------------------------------------
# UpdateURLHit
# Updates a URL hit with the correct status and message codes
# This is to be done after the data is processed in a view and the code has
# come to completion
#-------------------------------------------------------------------------------
def UpdateURLHit(hitID, responseCode, messageCode):   
    
    # Update the hit record
    Hit.objects.filter(pk=hitID).update(responseCode=str(responseCode),
                                           messageCode=messageCode)

    
#-------------------------------------------------------------------------------
# logServerEvent
# Handles analytics logging for server-side-triggered events.
#-------------------------------------------------------------------------------
def logServerEvent(eventTag, data):
    if (eventTag == Const.Tags.Events.PRUNE_LOCALPOSTS):
        _LogPruneLocalPostsEvent(data)
    
    elif (eventTag == Const.Tags.Events.PRUNE_MESSAGES):
        _LogPruneMessagesEvent(data)
    
    elif (eventTag == Const.Tags.Events.PRUNE_STATIC_CONTENT):
        _LogPruneStaticContentEvent(data)
    
    elif (eventTag == Const.Tags.Events.PRUNE_THREAD):
        _LogPruneThreadEvent(data)  
        
    elif (eventTag == Const.Tags.Events.SERVER_NOTIFICATION):
        _LogServerNotificationEvent(data)
        
#------------------------------------------------------------------------------ 
# Helper functions for server-side-triggered event logging
#------------------------------------------------------------------------------ 

def _LogPruneLocalPostsEvent(data):
    LocalPostsPrunedEvent.objects.create(messageCode=data[Const.DataCollection.ParamNames.MESSAGE_CODE],
                                           numOldPosts=data[Const.DataCollection.ParamNames.NUM_REQUESTED],
                                           numDeletedPosts=data[Const.DataCollection.ParamNames.NUM_DELETED])
def _LogPruneMessagesEvent(data):
    MessagesPrunedEvent.objects.create(messageCode=data[Const.DataCollection.ParamNames.MESSAGE_CODE],
                                           numOldMessages=data[Const.DataCollection.ParamNames.NUM_REQUESTED],
                                           numDeletedMessages=data[Const.DataCollection.ParamNames.NUM_DELETED])
    
def _LogPruneStaticContentEvent(data):
    StaticContentPrunedEvent.objects.create(messageCode=data[Const.DataCollection.ParamNames.MESSAGE_CODE],
                                           numRequestedForDeleteion=data[Const.DataCollection.ParamNames.NUM_REQUESTED],
                                           numDeleted=data[Const.DataCollection.ParamNames.NUM_DELETED])
    
def _LogPruneThreadEvent(data):
    ThreadPrunedEvent.objects.create(threadID=data[Const.DataCollection.ParamNames.THREAD_ID])
    
def _LogServerNotificationEvent(data):
    NotificationSentEvent.objects.create(messageCode=data[Const.DataCollection.ParamNames.MESSAGE_CODE],
                                               deliveryType=data[Const.DataCollection.ParamNames.DELIVERY_TYPE],
                                               notificationType=data[Const.DataCollection.ParamNames.NOTIFICATION_TYPE],
                                               numCollapsedNotifcations=data[Const.DataCollection.ParamNames.NUM_COLLAPSED_NOTIFICATIONS])
     
#-------------------------------------------------------------------------------
# logServerError
# Handles logging for all server errors and exceptions, given the python
# exception object. Logs in the database and also sends out notifications
#-------------------------------------------------------------------------------
def logServerError(exceptionObject):
    
    # pass object to utils function which will give us a dict of the info we need
    data = Utils.GetExceptionInfo(exceptionObject)
    
    newError = Error.objects.create(file=data[Const.DataCollection.ParamNames.FILENAME],
                               lineNum=data[Const.DataCollection.ParamNames.LINE_NUM],
                               exeptionMessage=data[Const.DataCollection.ParamNames.EXCEPTION_MESSAGE],
                               stackTrace=data[Const.DataCollection.ParamNames.STACK_TRACE])
    
    # Create a string out of the error and pass it to the notifier
    newErrorString = ServerErrorsToString(newError)
    Notifier.StartServerErrorReport(newErrorString)
    
#-------------------------------------------------------------------------------
# ServerErrorsToString
# Takes a queryset of server errors or a single server error query object 
# and creates a set of strings (or single string) of them formatted pretty.
#-------------------------------------------------------------------------------
def ServerErrorsToString(serverErrors):

    if (type(serverErrors) is QuerySet):
        stringList = []
        
        for error in serverErrors:       
            formattedError = _FormatServerError(error)
            stringList.append(formattedError)
        
        return stringList
    
    else:
        return _FormatServerError(serverErrors)
 
#-------------------------------------------------------------------------------
# Helper function for _ServerErrorsToString
#-------------------------------------------------------------------------------
def _FormatServerError(serverError):
    with io.StringIO() as buf, redirect_stdout(buf): # redirect print() into a string buffer
        Utils.PrintSoftStartLine()
        print('---ERROR ID: %s---' % Utils.BinaryToUUID(serverError.id))
        print('TIME: %s' % Utils.GetPrettyFormatTimestamp(serverError.timeCreated))
        print('FILE: %s | LINE: %s' % (serverError.file, serverError.lineNum))
        print('PROBLEM: %s' % serverError.exeptionMessage)
        print('TRACEBACK: %s' % serverError.stackTrace)
        Utils.PrintSoftEndLine()
    
        return buf.getvalue()
    

#-------------------------------------------------------------------------------
# DjangoMiddlewareErrorLogger
# Class to handle any exception thrown by django or python anywhere in the 
# middleware. Sends the exception object to the server error logger.
# This is meant to handle standard python-django exceptions. Exceptions 
#-------------------------------------------------------------------------------
class DjangoMiddlewareErrorLogger(logging.Handler):
    def __init__(self):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
    
    # emit catches the exception record object
    def emit(self, record):
        # Simply pass on the exeception object to be logged in the DB
        logServerError(record.exc_info[1])
        return
    

    

    
        

    