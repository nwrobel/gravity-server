#-------------------------------------------------------------------------------
# Notifier module
# Sends out notifications (email, text messages, etc)
# Sending out notifications takes times and needs to be handled async. so the
# client does not feel server lag. (this lag free part is under construction)
#
# Nick Wrobel
# Created: 1/4/16
# Modified: 2/9/16
#-------------------------------------------------------------------------------
 
import time
from django.conf import settings
from django.core.mail import send_mail
from JokrBackend.models import TimeLastNotifcationSent
import JokrBackend.Constants as Const
from django.core.exceptions import ObjectDoesNotExist
 
 
def StartServerErrorReport(errorString):
    # TODO: make this email sending async
    # TODO: make an email queue that sends notifications at max once per minute 
    # TODO: message notification collapsing into one email/text (multiple errors)
     
    # NOTE: this is a temporary patch until I get the more intellegent message
    # notification collapsing and queing code written.
    if (settings.EMAIL_NOTIFICATIONS):
         
        currentTime = time.time()
         
        # Check that we are not sending too fast
        try:
            entry = TimeLastNotifcationSent.objects.get(pk=1)
            earliestTimeAllowed = entry.timeLastSent + settings.MAX_TIME_BETWEEN_EMAILS_SEC
             
            # If we are allowed to send, then send the email
            if (currentTime >=  earliestTimeAllowed):
                _SendServerErrorEmail(errorString)
                entry.timeLastSent = currentTime
                entry.save()
             
        # If there has never been anything sent, create a new entry and send the email
        except ObjectDoesNotExist:
            TimeLastNotifcationSent.objects.create(timeLastSent=currentTime)
            _SendServerErrorEmail(errorString)
                         
                         
def _SendServerErrorEmail(errorString):
    send_mail('SERVER ERROR REPORT', errorString, settings.SENDER_EMAIL, settings.EMAIL_RECIPIENTS, fail_silently=False)
