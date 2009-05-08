from distutils.core import setup

setup(
    name='django-campaign',
    version=__import__('campaign').__version__,
    description='A basic newsletter app for the Django webframework',
    author='Arne Brodowski',
    author_email='arne@rcs4u.de',
    url='http://code.google.com/p/django-campaign/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages = (
        'campaign',
    ),
)