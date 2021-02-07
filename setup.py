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
        "pandora": ["data/*.*"]  # include all files in the data directory
    },
    install_requires=[
        'pandas~=1.2.1',
        'fnvhash~=0.1.0',
        'scikit-learn~=0.24.1',
        'workalendar~=14.1.0',
        'category-encoders~=2.2.2']
)
