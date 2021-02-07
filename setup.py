from distutils.core import setup

setup(
    name='pandora',
    version='0.1.0',
    packages=['pandora', 'pandora.data'],
    url='https://github.com/rbilleci/pandora',
    license='',
    author='Richard Billeci',
    author_email='rick.billeci@gmail.com',
    description='',
    package_data={
        "data": ["data/*.*"],  # include all files in the data directory
    }
)
