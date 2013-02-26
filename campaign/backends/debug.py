from campaign.backends.base import BaseBackend

class DebugBackend(BaseBackend):
    """ an example backend which just prints out the email instead of sending it

        NOTE: This backend is obsolete since Django now has a built-in 
        mechanism to print emails to the console. Just use the send_mail
        Backend and configure Django accordingly.
        
    """
    
    def send_mail(self, email, fail_silently=False):
        print "Subject: %s" % email.subject
        print "To: %s" % email.recipients()
        print "======"
        print email.message().as_string() # the actual email message
        print "======"
        return 0
        
backend = DebugBackend()