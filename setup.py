from setuptools import setup, find_packages

setup(name='gnip_insights_interface',
        packages=find_packages(),
        scripts=[
            'tweet_engagements.py',
            ],
        version='0.2',
        license='MIT',
        author='Jeff Kolb',
        author_email='jeffakolb@gmail.com',
        description="Interface to the Twitter Insights APIs", 
        url='https://github.com/jeffakolb/Gnip-Insights-Interface',
        install_requires=['pyyaml','requests','requests_oauthlib','python-dateutil'],
        )
