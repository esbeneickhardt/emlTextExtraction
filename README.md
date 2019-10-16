# Introduction

The environment to run this code is setup in a docker image, while the code to extract attachments and text from e-mails is setup in a jupyter notebook.

# Prerequsites
You need to have Docker installed!

# Setting up Environment

1. Build docker image  
Go to root folder and type **docker build --tag=emlTextExtraction:0.0.1 .**. 

This will take a while as a bunch of libraries and distributions are installed, including the email package and the textract, tesseract and ImageMagick distributions.

2. Run docker container  
Start the container by running **docker run -p 6969:6969 -v /path/to/root/folder/:/mnt/notebooks emlTextExtraction:0.0.1**.

This code starts up the container and makes jupyter availible through the browser at your local host. Docker should return the adress to type into your browser.

# Extracting text from eml-files
## TBD
