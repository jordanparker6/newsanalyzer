import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='newsreader',  
     version='0.1',
     scripts=['./newsreader/__main__.py'],
     author="Jordan Parker",
     author_email="jordanhparker6@gmail.com",
     description="A web-scraper, sentiment and entity analysis tool for market research",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/jordanparker6/newsreader",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     entry_points = {
        'console_scripts': ['newsreader=newsreader.__main__:main'],
    }
 )