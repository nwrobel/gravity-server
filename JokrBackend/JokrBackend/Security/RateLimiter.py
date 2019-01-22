#-------------------------------------------------------------------------------
# 
# Created: 2/15/16
#-------------------------------------------------------------------------------

import time
from JokrBackend.models import Thread, Reply
import JokrBackend.Constants as Const

#-------------------------------------------------------------------------------
# _UserLiveRateLimitExceeded
# Checks if the user is posting too fast to live, for moderation
# 
# params:
#    clientUserID - uuid of the client
# returns:
#     T/F if the user has posted too fast and needs to wait
#-------------------------------------------------------------------------------
def UserLiveRateLimitExceeded(clientUserID):
    
    currentTime = time.time()
    
    # Get all the timestamps for threads, as a flat list    
    postTimes = Thread.objects.values_list('timeCreated', flat=True) 
    postTimes = postTimes.filter(fromUser=clientUserID) # only from this user
    # order by time created, descending. Limit to the max # of replies we want to examine
    postTimes = postTimes.order_by('-timeCreated')[:Const.Views.UploadLocalPost.MAX_POSTS_WITHIN_TIMEFRAME] 

    # If there are at least x posts, check the min of the set against the current time
    if len(postTimes) == Const.Views.UploadThread.MAX_POSTS_WITHIN_TIMEFRAME:
        minPostTime = min(list(postTimes))
        timeToleranceSeconds = Const.Views.UploadLocalPost.TIMEFRAME_MINUTES * 60
        if (currentTime - minPostTime) < timeToleranceSeconds:
            return True
    
    # else
    return False

#-------------------------------------------------------------------------------
# _UserReplyRateLimitExceeded
# Checks whether or not this user has replied too much within the given time
# a moderation feature
# 
# params:
#     clientUserID - uuid of the client in question
#     currentTime - current timestamp
# returns:
#     T/F whether this user has posted too fast
#-------------------------------------------------------------------------------
def UserReplyRateLimitExceeded(clientUserID):
    
    currentTime = time.time()

    # Get all the timestamps for replies, as a flat list    
    replyTimes = Reply.objects.values_list('timeCreated', flat=True) 
    replyTimes = replyTimes.filter(fromUser=clientUserID) # only from this user
    # order by time created, descending. Limit to the max # of replies we want to examine
    replyTimes = replyTimes.order_by('-timeCreated')[:Const.Views.UploadReply.MAX_REPLIES_WITHIN_TIMEFRAME] 
        
    # If the user has made at least the max # of replies, then examine the timestamps
    # Check the min of the set against the current time
    if len(replyTimes) == Const.Views.UploadReply.MAX_REPLIES_WITHIN_TIMEFRAME:      
        minPostTime = min(replyTimes)
        timeToleranceSeconds = Const.Views.UploadReply.TIMEFRAME_MINUTES * 60
         
        if (currentTime - minPostTime) < timeToleranceSeconds:
            return True
    # else
    return False