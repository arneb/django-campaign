from django.dispatch import Signal


campaign_sent = Signal(providing_args=["campaign"])
