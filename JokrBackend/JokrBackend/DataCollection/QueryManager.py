#-------------------------------------------------------------------------------
# QueryManager module
# Contains common routines that query and update the database. 
# 
# Nick Wrobel
# Created: 2/15/16
# Modified: 2/16/16
#-------------------------------------------------------------------------------

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import JokrBackend.Constants as Const
from JokrBackend.models import Thread, OnlineContent, ArchivedContent
from JokrBackend.Custom import Utils

#-------------------------------------------------------------------------------
# GetLiveThreadsByTimeCreated
# Returns the queryset of all online threads, ordered by the timeLastActive
# (bump time), which is a property on the Thread model.
# 
# Params (optional):
#    limit - how many threads to limit the results to
#    ascending - should the list be sorted in ascending (least timeLastActive first)
# 
# Returns:
#    the queryset of threads
#-------------------------------------------------------------------------------
def GetLiveThreadsByTimeLastActive(limit=None, ascending=False):
    
    # Gets all threads, sorted by timeLastActive, which is a property on 
    # the Thread model
    if (limit):
        threads = sorted (Thread.objects.all (), 
                      key = lambda p: p.timeLastActive, 
                      reverse=(not ascending))[:limit]
    else:
        threads = sorted (Thread.objects.all (), 
                      key = lambda p: p.timeLastActive, 
                      reverse=(not ascending))
        
    return threads

#-------------------------------------------------------------------------------
# CheckAndPruneThreads
# Checks if the thread limit on a board is hit. If so, it prunes the thread
# that was least recently created
#
# params:
#     none
# returns:
#    nothing 
#-------------------------------------------------------------------------------
def CheckAndPruneThreads():
    import JokrBackend.DataCollection.ContentManager as ContentManager
    import JokrBackend.DataCollection.DataCollector as DataCollector

    # get the thread count
    numOfCurrentThreads = Thread.objects.count()
    
    # If the board is full already, prune a thread
    if numOfCurrentThreads > settings.BOARD_THREAD_LIMIT:
        numThreadsToPrune = numOfCurrentThreads - settings.BOARD_THREAD_LIMIT
        
        # Get the lowest bump order threads to be pruned
        threadsToPrune = GetLiveThreadsByTimeLastActive(ascending=True, limit=numThreadsToPrune)
        
        for thread in threadsToPrune:
              
            # log info about the pruned thread
            DataCollector.logServerEvent(Const.Tags.Events.PRUNE_THREAD, {
                Const.DataCollection.ParamNames.THREAD_ID: thread.id  })
                                         
            ContentManager.DeleteContent(thread.id)
            
#-------------------------------------------------------------------------------
# GetThreadReplies
# Returns the set of replies for a given thread
#-------------------------------------------------------------------------------
def GetThreadReplies(threadID):
    from JokrBackend.models import Reply
    
    return Reply.objects.filter(parentThread=Utils.UUIDToBinary(threadID))
                    
#-------------------------------------------------------------------------------
# GetObject
# A wrapper for the .get() query method. Gets the object from the database 
# or returns null
# Params:
#    model - the django model class
#    other arguments (same args as to .get())
# Returns:
#    the object, or null
#-------------------------------------------------------------------------------
def GetObject(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
    
#-------------------------------------------------------------------------------
# GetObjectByID
# A wrapper for the .get() query method. Gets the object from the database 
# or returns null. Converts the string uuid into binary so the query works.
# Params:
#    model - the django model class
#    other arguments (same args as to .get())
# Returns:
#    the object, or null
#-------------------------------------------------------------------------------
def GetObjectByID(model, uuid):
    try:
        return model.objects.get(id=Utils.UUIDToBinary(uuid))
    except model.DoesNotExist:
        return None
    
#-------------------------------------------------------------------------------
# ContentIsArchived
# Determines if a piece of content is 'archived' or not
#-------------------------------------------------------------------------------
def ContentIsArchived(cid):
    if (GetObjectByID(ArchivedContent, cid)):
        return True
    # else
    return False
    
#-------------------------------------------------------------------------------
# ContentIsOnline
# Determines if a piece of content is 'online' or not
#-------------------------------------------------------------------------------
def ContentIsOnline(cid):
    if (GetObjectByID(OnlineContent, cid)):
        return True
    # else
    return False
    
#-------------------------------------------------------------------------------
# Determines if a user is currently under a global ban.  
# 
# Params:
#    user - the user object
# Returns: T/F if the user is currently banned
#-------------------------------------------------------------------------------
def UserIsBanned(user):
    import time
    from JokrBackend.models import Ban
    
    currentTime = time.time()
    
    # Get the most recent user ban
    userBan = Ban.objects.filter(bannedUser=user).order_by('-timeCreated')[:1]
     
    # If there is a ban, check its expiration
    if(userBan):
        if (userBan[0].timeExpires > currentTime):
            return True
    # else
    return False

#-------------------------------------------------------------------------------
# Gets the most recent moderation action for a piece of content.
# Important thing to note: there can be multiple mod actions for a single piece 
# of content. However, each report will ultimately have one mod action that is 
# the 'most current' action taken for the content.
#-------------------------------------------------------------------------------
def GetMostRecentModActionResult(contentID):
    from JokrBackend.models import ModAction

    # get the most recent mod action 
    modActionType = ModAction.objects.filter(cid=contentID).order_by('timeCreated')[:1]
     
    # if it exists, return the mod action result
    if (modActionType):
        modActionType = modActionType[0]
        return modActionType.result
     
    else:
        return ''
    

