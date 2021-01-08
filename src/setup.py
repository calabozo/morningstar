from setuptools import setup

setup(name='pyfunds',
      version='0.1',
      description='Money investment analysis',
      author='Flying Circus',
      license='GPL2',
      packages=['pyfunds'],
      install_requires=[
          'pandas','numpy','dryscrape','beautifulsoup4','requests'
      ],
      scripts=['bin/download_forecast'],
      zip_safe=False)

