import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='pyfunds',
      version='0.1.2-4',
      description='Money investment analysis',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Flying Circus',
      license='GPL2',
      packages=['pyfunds'],
      install_requires=[
          'pandas','numpy','dryscrape','beautifulsoup4','requests'
      ],      
      scripts=['bin/download_forecast'],
      zip_safe=False)

