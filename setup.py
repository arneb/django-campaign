from distutils.core import setup

setup(
    name='django-campaign',
    version=__import__('campaign').__version__,
    description='A basic newsletter app for the Django webframework',
    long_description=open('docs/index.txt').read(),
    author='Arne Brodowski',
    author_email='arne@rcs4u.de',
    license="BSD",
    url='http://code.google.com/p/django-campaign/',
    download_url='http://code.google.com/p/django-campaign/downloads/list',
    classifiers=[
        'Development Status :: 4 - Beta',
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
    package_data = {
        'campaign': 
            ['templates/admin/campaign/campaign/*.html',
             'templates/campaign/*.html'],
    }
)