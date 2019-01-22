#-------------------------------------------------------------------------------
# Module for working with static content hosted on a 3rd party service.
# Currently, we are using Amazon's S3 for static files.
# 
# Nick Wrobel
# Created: 10/30/15
# Modified: 11/6/15
#-------------------------------------------------------------------------------

import boto3
import JokrBackend.DataCollection.DataCollector as DataCollector
import JokrBackend.Constants as Const
from django.conf import settings
import subprocess


#-------------------------------------------------------------------------------
# DeleteStaticContent
# Deletes static files from the 3rd party hoster
# 
# params:
#    urls: a list of filename key (coming from the database)
# returns:
#    True - success
#    False - error
#-------------------------------------------------------------------------------
def DeleteStaticContent(urls):
    TAG = Const.Tags.Events.PRUNE_STATIC_CONTENT
    
    try:
        if(settings.PRUNE_STATIC_CONTENT):
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(settings.AWS_BUCKET_NAME)
        
            objectsToDelete = []
                   
        
            # build up the list of objects to delete to we can pass to the delete
            for url in urls:
                object = { 'Key': url}
                objectsToDelete.append(object)
            
            delete = {'Objects': objectsToDelete,
                      'Quiet': False }
            
            # Delete the objects from the bucket
            # TODO: parse this response object and do stuff with it 
            response = bucket.delete_objects(Delete=delete)
            
            DataCollector.logServerEvent(TAG, { 
                Const.DataCollection.ParamNames.MESSAGE_CODE: Const.DataCollection.MessageCodes.Events.PruneStaticContent.SUCCESS,
                Const.DataCollection.ParamNames.NUM_RECEIVED: len(urls),
                Const.DataCollection.ParamNames.NUM_DELETED: len(urls) }) # note: we need to get this info from response object later
            
    except Exception as e:
        DataCollector.logServerError(e)
        

#-------------------------------------------------------------------------------
# DownloadStaticContent
# Downloads static content from S3
# 
# Params:
#     key - the S3 key
#     getFromArchive - T/F whether or not we should look for the key in the archive bucket
#     downloadDir - where to download the file to
#-------------------------------------------------------------------------------
def DownloadStaticContent(key, getFromArchive, downloadDir):
    s3 = boto3.client('s3')
    newFilePath = downloadDir + key 
    
    if (getFromArchive):
        s3.download_file(settings.AWS_ARHCIVE_BUCKET_NAME, key, newFilePath)
    else:
        s3.download_file(settings.AWS_BUCKET_NAME, key, newFilePath)
        
#-------------------------------------------------------------------------------
# ArchiveStaticContent
# Moves static content from the 'live data' bucket into the archive bucket
#-------------------------------------------------------------------------------
def ArchiveStaticContent(key):
    sourceFile = 's3://' + settings.AWS_BUCKET_NAME + '/' + key
    destFile = 's3://' + settings.AWS_ARHCIVE_BUCKET_NAME + '/'
    
    subprocess.call(['s3cmd', 'cp', sourceFile, destFile]) # copy the file over to archive bucket
    
    


        

    
    