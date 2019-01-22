import time

class SecurityProperties:
    def __init__(self):
        # Info for logging
        self.hitID = ''
        self.clientIP = '' 
        self.timestamp = time.time()
        self.requestedURL = ''
        self.requestMethod = ''
        self.requestContentType = ''
        self.requestData = ''
        
        # Custom headers, if present
        self.userID = ''
        self.sessionToken = ''
        
        # Info extracted about the client, for optimization
        self.userObject = None # DB object of the user 
        self.userSession = None  # DB object of the session
        self.jsonRequestData = {} # Decoded dictionary of json params
        
        # Info on security and possible security issues
        self.isSecure = False # Is there a security issue     
        self.errorsList = []
        
        # resulting httpResponse (generated from the HttpResponseFactory)
        self.httpResponse = None
        
        
    