# an example backend which just prints out the email instead of sending it

class DebugBackend(object):
    def send_mail(self, email, fail_silently=False):
        print "Subject: %s" % email.subject
        print "To: %s" % email.recipients()
        print "======"
        print email.message().as_string() # the actual email message
        print "======"
        return 0
        
backend = DebugBackend()