import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='pyfunds',
      version='0.1',
      description='Money investment analysis',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='JMG Calabozo',
      license='GPL2',
      packages=['pyfunds'],
      install_requires=[
          'pandas','numpy','dryscrape','beautifulsoup4','requests','Deprecated'
      ],
      zip_safe=False)

