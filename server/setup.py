import platform
from setuptools import setup, find_packages

# data directory for windows
if platform.system() == "Windows":
    data_dir = 'c:\\www\\'
    fab = ''
else:
    data_dir = '/var/www_apps/'
    fab = 'Fabric'

setup(
    name='beerlog',
    version='0.01',
    long_description=__doc__,
    packages=['beerlog',],
    include_package_data=True,
    zip_safe=False,
    data_files=[(data_dir, ['beerlog.wsgi',
                            'beer_data.xml',
                            'styleguide2008.xml'])],
    install_requires=['Flask',
                      'PIL',
                      'Boto',
                      fab,
                      'python-dateutil==1.5',
                      'M2Crypto',
                      'SQLObject'],
    )
