#-------------------------------------------------------------------------------
# Module for custom django model fields
# 
# Nick Wrobel
# Created: 7/28/15
# Modified: 11/6/15
#-------------------------------------------------------------------------------

from django.db import models

#---------------------------------------------------------------------------- 
# UUIDField
#------------------------------------------------------------------------------ 
class UUIDField(models.Field, metaclass=models.SubfieldBase):
          
    # Note: this simply puts/gets whatever into the DB. Type checking should be 
    # done on the client's data, and binary-string convertions should be done 
    # with the Utils module.
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 16
        super(UUIDField, self).__init__(*args, **kwargs)
 
    def db_type(self, connection):
        return 'binary(16)'
    
    
        

    


    
    