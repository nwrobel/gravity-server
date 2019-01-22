#-------------------------------------------------------------------------------
# Security Actuator module
# Used to take action against a security threat.
# Think of this as security guards chasing you down and handcuffing you.
# 
# Nick Wrobel
# Created: 9/24/15
# Modified: 11/6/15
#-------------------------------------------------------------------------------

import JokrBackend.DataCollection.DataCollector as DataCollector

def TakeSecurityAction(securityProperties):
    
    # simply log the error
    DataCollector.logSecurityError(securityProperties)
    
    
        
