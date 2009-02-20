from django.core.mail import SMTPConnection



class SMTPQueue(SMTPConnection):
    """
    Can be used instead of Django's SMTPConnection class to queue
    a bunch of emails for later sending.
    """
    
    def __init__(self, *args, **kwargs):
        super(SMTPQueue, self).__init__(*args, **kwargs)
        self._email_messages = []
        
        
    def send_messages(self, email_messages):
        """
        Queues one or more EmailMessage objects and returns the number of email
        messages queued.
        """
        if not email_messages:
            return
        
        num_sent = 0
        for message in email_messages:
            sent = self._queue(message)
            if sent:
                num_sent += 1
        return num_sent
        
    
    def _queue(self, email_message):
        self._email_messages.append(email_message)
    
    
    def defer(self):
        """
        Save the state of this Queue for later sending
        """
        try:
            import cPickle as pickle
        except ImportError:
            import pickle
        
        return pickle.dumps(self)
        
        
    def flush(self):
        """
        Will send all queued EmailMessage objects.
        """
        if not self._email_messages:
            return
        new_conn_created = self.open()
        if not self.connection:
            # We failed silently on open(). Trying to send would be pointless.
            return
        num_sent = 0
        for message in self._email_messages:
            sent = self._send(message)
            if sent:
                num_sent += 1
        if new_conn_created:
            self.close()
        #print "sent: %s" % num_sent
        return num_sent
        

class SMTPLoggingConnection(SMTPConnection):
    """
    Logs bounces etc.
    
    """
    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        from campaign.models import BounceEntry
        if not email_messages:
            return
        new_conn_created = self.open()
        if not self.connection:
            # We failed silently on open(). Trying to send would be pointless.
            return
        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
            except Exception, e:
                BounceEntry.objects.create(email=message.recipients()[0], exception=str(e))
                sent = False
            if sent:
                num_sent += 1
        if new_conn_created:
            self.close()
        return num_sent
        