#-------------------------------------------------------------------------------
# Content archival module
#
# Nick Wrobel
# Created: 12/12/15
# Modified: 2/12/15
#-------------------------------------------------------------------------------

from django.core.exceptions import ObjectDoesNotExist
from JokrBackend.models import PostableContent, ArchivedPostableContent, LocalPost, Message, Thread, Reply, LocalPostArchive, MessageArchive, ThreadArchive, ReplyArchive
import JokrBackend.Custom.StaticContentUtils as StaticContentUtils
import JokrBackend.Constants as Const

def ArchiveContent(cid):
    content = PostableContent.objects.get(pk=cid)
     
    if (content.contentType == Const.Tags.ContentTypes.LOCALPOST):
        _ArchiveLocalPost(content)
        
    elif (content.contentType == Const.Tags.ContentTypes.MESSAGE):
        _ArchiveMessage(content)
        
    elif (content.contentType == Const.Tags.ContentTypes.THREAD):
        _ArchiveThread(content)
        
    elif (content.contentType == Const.Tags.ContentTypes.REPLY):
        _ArchiveReply(content)
      
                                                                
def _ArchiveLocalPost(content):
    localPost = LocalPost.objects.get(pk=content.id)
    
    # Check if the post exists in the archive
    archivedPost = ArchivedPostableContent.objects.filter(pk=content.id)
        
    # If it does not exist, continue
    if (not archivedPost):     
        LocalPostArchive.objects.create(pk=content.id,
                                        timeCreated=content.timeCreated,
                                        fromUser=content.fromUser,
                                        contentType=content.contentType,
                                        url=content.url,
                                        latitude=localPost.latitude,
                                        longitude=localPost.longitude,
                                        text=localPost.text)

    # S3 operations
    StaticContentUtils.ArchiveStaticContent(content.url)

def _ArchiveMessage(content):
    message = Message.objects.get(pk=content.id)
    
    # Check if the message exists in the archive
    archivedPost = ArchivedPostableContent.objects.filter(pk=content.id)
        
    # If it does not exist, continue
    if (not archivedPost):
        MessageArchive.objects.create(pk=content.id,
                                      timeCreated=content.timeCreated,
                                        fromUser=content.fromUser,
                                        contentType=content.contentType,
                                        url=content.url,
                                        toUser=message.toUser,
                                        text=message.text)
    
    # S3 operations
    StaticContentUtils.ArchiveStaticContent(content.url)

def _ArchiveThread(content):
    thread = Thread.objects.get(pk=content.id)
    
    # Check if the thread exists in the archive
    existingThreadArchive = ThreadArchive.objects.filter(pk=content.id)
        
    # If it does exit, then we might need to update the archive
    if (existingThreadArchive):
        existingThreadArchive = existingThreadArchive[0]
        
        # get the replies for the original thread and the archived (old) version
        # of the thread
        existingReplyIDs = Reply.objects.filter(parentThread=thread).values_list('cid', flat=True)
        exisitngArchivedReplyIDs = ReplyArchive.objects.filter(parentThread=existingThreadArchive).values_list('archiveID', flat=True)
        
        newReplyToArchiveIDs = set(existingReplyIDs) - set(exisitngArchivedReplyIDs)
        
        # Archive each new reply 
        for newReplyToArchiveID in newReplyToArchiveIDs:
            # Get the new reply object from the ID
            newReplyToArchive = Reply.objects.get(pk=newReplyToArchiveID)
            
            # Create a thread archive for each thread, and attach this thread 
            # as each one's parent thread
            ReplyArchive.objects.create(timeCreated=newReplyToArchive.timeCreated,
                                        fromUser=newReplyToArchive.fromUser,
                                        contentType=newReplyToArchive.contentType,
                                        url=newReplyToArchive.url,
                                        name=newReplyToArchive.name,
                                        text=newReplyToArchive.text,
                                        parentThread=existingThreadArchive)
            
            StaticContentUtils.ArchiveStaticContent(newReplyToArchive.url)
  
    # If the archive does not exist, then we need to create it
    # We will save the thread and all of its replies
    else:  
        # Get the replies from the new thread
        threadReplies = Reply.objects.filter(parentThread=thread)
        
        newThreadArchive = ThreadArchive.objects.create(pk=content.id,
                                                            timeCreated=content.timeCreated,
                                                            fromUser=content.fromUser,
                                                            contentType=content.contentType,
                                                            url=content.url,
                                                            name=thread.name,
                                                            title=thread.title,
                                                            text=thread.text,
                                                            replyCount=thread.replyCount,
                                                            uniquePostersCount=thread.uniquePostersCount,
                                                            imageReplyCount=thread.imageReplyCount)
        
        StaticContentUtils.ArchiveStaticContent(content.url)

        
        # Create a new reply archive for each reply in the archived thread
        for reply in threadReplies:
            ReplyArchive.objects.create(timeCreated=reply.timeCreated,
                                        fromUser=reply.fromUser,
                                        contentType=reply.contentType,
                                        url=reply.url,
                                        name=reply.name,
                                        text=reply.text,
                                        parentThread=newThreadArchive)
            
            StaticContentUtils.ArchiveStaticContent(reply.url)


def _ArchiveReply(content):
    reply = Reply.objects.get(pk=content.id)
        
    # Check if the reply exists in the archive
    archivedReply = ReplyArchive.objects.filter(pk=content.id)
            
    # If it does not exist, continue
    if (not archivedReply):
        # check if the parent thread is in the archive
        parentThread = reply.parentThread
        
        archivedParentThread = ThreadArchive.objects.filter(pk=parentThread.id)
        
        # If the parent thread is already archived, then set this thread as 
        # the new parent thread and archive the reply
        if (archivedParentThread):
            archivedParentThread = archivedParentThread[0]
            
            ReplyArchive.objects.create(pk=content.id,
                                        timeCreated=content.timeCreated,
                                        fromUser=content.fromUser,
                                        contentType=content.contentType,
                                        url=content.url,
                                        name=reply.name,
                                        text=reply.text,
                                        parentThread=archivedParentThread)
        
        # If the parent thread is not archived, then we have to archive it
        # along with the reply
        else:
            # archive the parent thread
            newArchivedThread = ThreadArchive.objects.create(pk=content.id,
                                        timeCreated=parentThread.timeCreated,
                                        fromUser=parentThread.fromUser,
                                        contentType=parentThread.contentType,
                                        url=parentThread.url,
                                        name=parentThread.name,
                                        title=parentThread.title,
                                        text=parentThread.text,
                                        replyCount=parentThread.replyCount,
                                        uniquePostersCount=parentThread.uniquePostersCount,
                                        imageReplyCount=parentThread.imageReplyCount,
                                        timeOfLastReply=parentThread.timeOfLastReply)
            
            # archive the thread on s3
            StaticContentUtils.ArchiveStaticContent(parentThread.url)

            
            # archive the reply       
            ReplyArchive.objects.create(pk=content.id,
                                        timeCreated=content.timeCreated,
                                        fromUser=content.fromUser,
                                        contentType=content.contentType,
                                        url=content.url,
                                        name=reply.name,
                                        text=reply.text,
                                        parentThread=newArchivedThread)
        
        # Archive the reply on s3   
        StaticContentUtils.ArchiveStaticContent(content.url)

        
    
    