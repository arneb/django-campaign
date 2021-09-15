def recipient(recipient):
    return {'recipient': recipient}


def recipient_dict(recipient):
    recipient_dict = {}
    for k,v in recipient.__dict__.items():
        if not k.startswith("_") and k in ('first_name', 'last_name', 'email',
                'is_active', 'is_staff'):
            recipient_dict.update({'recipient_%s' % k: v})
    return recipient_dict
