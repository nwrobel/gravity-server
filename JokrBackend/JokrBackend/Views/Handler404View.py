#-------------------------------------------------------------------------------
# Handler404View
# This view is called whenever a 404 occurs in our app.
#
# Nick Wrobel
# Created: 9/28/15
# Modified: 10/8/15
#-------------------------------------------------------------------------------

import JokrBackend.Constants as Const
from JokrBackend.Security.SecurityChecker import RunThroughSecurityLayer 


def Handler404(requestData):
    
    TAG = Const.Tags.Urls.HANDLER_404
    
    # Put the 404 view through the security layer first. This will allow us to
    # take desired actions
    securityProperties = RunThroughSecurityLayer(TAG, requestData)
    
    # Simply return the security error
    return securityProperties.httpResponse
    