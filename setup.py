import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
     name='newsreader',  
     version='0.2',
     scripts=['./newsreader/__main__.py'],
     license="MIT",
     author="Jordan Parker",
     author_email="jordanhparker6@gmail.com",
     description="A web-scraper, sentiment and entity analysis tool for market research",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/jordanparker6/newsreader",
     packages=setuptools.find_packages(),
     install_requires=requirements,
     keywords=["Market Research", "Sentiment Analysis", "News"],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     entry_points = {
        'console_scripts': ['newsreader=newsreader.__main__:main'],
    }
 )