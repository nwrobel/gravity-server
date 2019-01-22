#===============================================================================
# Module for all models
# 
# Nick Wrobel
# Created: 4/27/15
# Modified: 2/15/16
#===============================================================================

from django.db import models
import JokrBackend.Constants as Const
import JokrBackend.Custom.Utils as Utils
from JokrBackend.Custom.ModelFields import UUIDField

#*******************************************************************************
# Client Analytics models
# Useful for behavior and usage tracking.
#*******************************************************************************
    
#*******************************************************************************
# Logging models
# Used for logging of server-side events
#*******************************************************************************    
class Error(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    file = models.CharField(max_length=Const.Database.MaxLengths.Logging.SERVER_ERROR_FILENAME, default=None, null=False)
    lineNum = models.IntegerField(default=None, null=False)
    exeptionMessage = models.TextField(default=None, null=False)
    stackTrace = models.TextField(default=None, null=False)
     
    class Meta:
        db_table = Const.Database.TableNames.Logging.ERROR
        
class ThreadPrunedEvent(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)  
    threadID = UUIDField(default=None, null=False)

    class Meta:
        db_table = Const.Database.TableNames.Logging.THREAD_PRUNED
    
class LocalPostsPrunedEvent(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    messageCode = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.MESSAGE_CODE)
     
    numOldPosts = models.IntegerField(default=None, null=False)
    numDeletedPosts = models.IntegerField(default=None, null=False)
     
    class Meta:
        db_table = Const.Database.TableNames.Logging.LOCALPOSTS_PRUNED
     
class MessagesPrunedEvent(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    messageCode = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.MESSAGE_CODE)
     
    numOldMessages = models.IntegerField(default=None, null=False)
    numDeletedMessages = models.IntegerField(default=None, null=False)
           
    class Meta:
        db_table = Const.Database.TableNames.Logging.MESSAGES_PRUNED
         
class StaticContentPrunedEvent(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    messageCode = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.MESSAGE_CODE)
     
    numRequestedForDeleteion = models.IntegerField(default=None, null=False)
    numDeleted = models.IntegerField(default=None, null=False)
     
    class Meta:
        db_table = Const.Database.TableNames.Logging.STATIC_CONTENT_PRUNED
         
class NotificationSentEvent(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    messageCode = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.MESSAGE_CODE)
     
    deliveryType = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Logging.NOTIFICATION_DELIVERY_TYPE)
    notificationType = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Logging.NOTIFICATION_TYPE)
    numCollapsedNotifcations = models.IntegerField(default=None, null=False) # how many 'notifications' are bundled into this one (many server errors sent in one email, for ex)
     
    class Meta:
        db_table = Const.Database.TableNames.Logging.NOTIFICATION_SENT

#*******************************************************************************
# Security Models
# Models used for client tracking and security
#*******************************************************************************
class User(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    
    # denormalized field
    timeLastLogin = models.IntegerField(default=None, null=True)
     
    class Meta:
        db_table = Const.Database.TableNames.Security.USER
        
class Session(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    timeExpires = models.IntegerField(default=None, null=False)
    token = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Security.SESSION_TOKEN)
    fromUser = models.ForeignKey(User, related_name='+', default=None, null=False)
     
    class Meta:
        db_table = Const.Database.TableNames.Security.SESSION
        
class Hit(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    url = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Security.ERROR_REQUESTED_URL)
    responseCode = models.SmallIntegerField(default=None, null=True)
    messageCode = models.CharField(default=None, null=True, max_length=Const.Database.MaxLengths.MESSAGE_CODE)
    ip = models.GenericIPAddressField(default=None, null=False)
    fromUser = models.ForeignKey(User, related_name='+', default=None, null=True)
    session = models.ForeignKey(Session, related_name='+', default=None, null=True)

    class Meta:
        db_table = Const.Database.TableNames.Security.HIT
        
class SecurityErrorHit(Hit):
    hit = models.OneToOneField(Hit, parent_link=True)
    requestMethod = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Security.ERROR_REQUEST_METHOD)
    requestContentType = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Security.ERROR_REQUEST_CONTENT_TYPE)
    requestData = models.TextField(default=None, null=False) 
    errors = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Security.ERROR_CHECK_RESULT)

    class Meta:
        db_table = Const.Database.TableNames.Security.HIT_SECURITY_ERROR
            
#*******************************************************************************
# Content Models
# Database content that is critical to make the core features of the app run.
#*******************************************************************************
class OnlineContent(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False) 
    fromUser = models.ForeignKey(User, related_name='+', default=None, null=False)
    fromSession = models.ForeignKey(Session, related_name='+', default=None, null=False) 
    key = models.CharField(default=None, null=True, max_length=Const.Database.MaxLengths.S3_KEY)
    contentType = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.CONTENT_TYPE)
    fav = models.BooleanField(default=False, null=False)
 
    class Meta:
        db_table = Const.Database.TableNames.Content.ONLINE
    
class LocalPost(OnlineContent):
    onlineContent = models.OneToOneField(OnlineContent, parent_link=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True, default=None, null=False)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True, default=None, null=False)
    text = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Content.LOCALPOST_TEXT)
    arn = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.AWS_ARN)
     
    class Meta:
        db_table = Const.Database.TableNames.Content.ONLINE_LOCALPOST
         

class Message(OnlineContent):
    onlineContent = models.OneToOneField(OnlineContent, parent_link=True)
    toUser = models.ForeignKey(User, related_name='+', default=None, null=False)
    text = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Content.MESSAGE_TEXT)
  
    class Meta:
        db_table = Const.Database.TableNames.Content.ONLINE_MESSAGE
         
class Thread(OnlineContent):
    onlineContent = models.OneToOneField(OnlineContent, parent_link=True)
    text = models.CharField(max_length=Const.Database.MaxLengths.Content.THREAD_TEXT, default=None, null=False)
    arn = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.AWS_ARN)
    
    # A getter for the timeLastActive value
    # Queries the thread's replies to find the bump time of the thread
    def getTimeLastActive(self):
        
        # Get all timeCreated values for the thread's reply
        repliesTimesLastActive = Reply.objects.filter(parentThread=self).values_list('timeCreated', flat=True)
        
        # If replies exist, use the max timeCreated as the timeLastActive
        if (repliesTimesLastActive):
            timeLastActive = max(list(repliesTimesLastActive))
        # Otherwise, use the time the thread was created
        else:
            timeLastActive = self.onlineContent.timeCreated
        
        return timeLastActive
    timeLastActive = property(getTimeLastActive)
    
    # A getter for the replyCount value 
    # Simply counts the replies to this thread
    def getReplyCount(self):
        
        replyCount = Reply.objects.filter(parentThread=self).count()
        return replyCount
    replyCount = property(getReplyCount)
    
    # A getter for the uniquePostersCount value
    def getUniquePostersCount(self):
        
        uniqueCount = Reply.objects.filter(parentThread=self).values_list('fromUser_id', flat=True).distinct()
        return len(uniqueCount)
    uniquePostersCount = property(getUniquePostersCount)
     
    class Meta:
        db_table = Const.Database.TableNames.Content.ONLINE_THREAD
              
class Reply(OnlineContent):
    onlineContent = models.OneToOneField(OnlineContent, parent_link=True)
    parentThread = models.ForeignKey(Thread, related_name='+', default=None, null=False)
    text = models.CharField(max_length=Const.Database.MaxLengths.Content.REPLY_TEXT, default=None, null=True)
      
    class Meta:
        db_table = Const.Database.TableNames.Content.ONLINE_REPLY
     
class ArchivedContent(models.Model):
    id = UUIDField(primary_key=True, default=None, null=False)
    timeArchived = models.IntegerField(default=Utils.CreateTimestampForDB, null=False) 
    timeOriginalCreated = models.IntegerField(default=None, null=False) 
    fromUser = models.ForeignKey(User, related_name='+', default=None, null=False)
    fromSession = models.ForeignKey(Session, related_name='+', default=None, null=False)
    key = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.S3_KEY)
    contentType = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.CONTENT_TYPE)
    fav = models.BooleanField(default=False, null=False)
     
    class Meta:
        db_table = Const.Database.TableNames.Content.ARCHIVED
     
class ArchivedLocalPost(ArchivedContent):
    archivedContent = models.OneToOneField(ArchivedContent, parent_link=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True, default=None, null=False)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True, default=None, null=False)
    text = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Content.LOCALPOST_TEXT)
     
    class Meta:
        db_table = Const.Database.TableNames.Content.ARCHIVED_LOCALPOST
         
class ArchivedMessage(ArchivedContent):
    archivedContent = models.OneToOneField(ArchivedContent, parent_link=True)
    toUser = models.ForeignKey(User, related_name='+', default=None, null=False)
    text = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Content.MESSAGE_TEXT)
     
    class Meta:
        db_table = Const.Database.TableNames.Content.ARCHIVED_MESSAGE
 
class ArchivedThread(ArchivedContent):
    archivedContent = models.OneToOneField(ArchivedContent, parent_link=True)
    arn = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.AWS_ARN)
    text = models.CharField(max_length=Const.Database.MaxLengths.Content.THREAD_TEXT, default=None, null=False)
      
    class Meta:
        db_table = Const.Database.TableNames.Content.ARCHIVED_THREAD
          
class ArchivedReply(ArchivedContent):
    archivedContent = models.OneToOneField(ArchivedContent, parent_link=True)
    parentThread = models.ForeignKey(ArchivedThread, related_name='+', default=None, null=False)
    text = models.CharField(max_length=Const.Database.MaxLengths.Content.REPLY_TEXT, default=None, null=True)
      
    class Meta:
        db_table = Const.Database.TableNames.Content.ARCHIVED_REPLY
   
#*******************************************************************************
# Moderation models
# Database content that is used for moderation
#*******************************************************************************
class Block(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)
    blockerUser = models.ForeignKey(User, related_name='+', default=None, null=False)
    blockedUser = models.ForeignKey(User, related_name='+', default=None, null=False)
     
    class Meta:
        db_table = Const.Database.TableNames.Moderation.BLOCK
 
class ModAction(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False) 
    result = models.CharField(default=None, null=False, max_length=3)
    contentID = UUIDField(default=None, null=False)
    contentType = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.CONTENT_TYPE)

    class Meta:
        db_table = Const.Database.TableNames.Moderation.MOD_ACTION
     
class Report(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False) 
    fromUser = models.ForeignKey(User, related_name='+', default=None, null=False)
    contentID = UUIDField(default=None, null=False)
    modAction = models.ForeignKey(ModAction, related_name='+', default=None, null=True)
    contentType = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.CONTENT_TYPE)
  
    class Meta:
        db_table = Const.Database.TableNames.Moderation.REPORT
 
class Ban(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False) 
    timeBanExpires = models.IntegerField(default=None, null=False)
    bannedUser = models.ForeignKey(User, related_name='+', default=None, null=False) 
     
    class Meta:
        db_table = Const.Database.TableNames.Moderation.BAN

#*******************************************************************************
# analytics models
#*******************************************************************************
class Feedback(models.Model):
    id = UUIDField(primary_key=True, default=Utils.CreateSequentialUUIDForDB, null=False)
    timeCreated = models.IntegerField(default=Utils.CreateTimestampForDB, null=False)        
    fromUser = models.ForeignKey(User, related_name='+', default=None, null=False) 
    text = models.CharField(default=None, null=False, max_length=Const.Database.MaxLengths.Analytics.FEEDBACK)
    
    class Meta:
        db_table = Const.Database.TableNames.Analytics.FEEDBACK


#-------------------------------------------------------------------------------
# Temp table to store a single value: the time that an email notifcation
# was just sent out. This is a hack to prevent thousands of emails from being
# sent and killing the server
#-------------------------------------------------------------------------------
class TimeLastNotifcationSent(models.Model):
    timeLastSent = models.IntegerField(default=None, null=False)
     
    class Meta:
        db_table = Const.Database.TableNames.NOTIFICATION_TEMP_TIME_LAST_SENT
         


        

        

        
