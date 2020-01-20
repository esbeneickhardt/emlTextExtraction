# Introduction

The environment to run this code is set up in a docker image, while the code to extract attachments and text from e-mails found in the modules directory. As the docker image has Jupyter Notebook installed, the process of extracting texts from e-mails and their attachments can easily be done using Notebooks.

# Prerequsites
You need to have Docker installed!

# Setting up Environment

1. Build docker image  
Go to root folder and type **docker build --tag=eml_text_extraction:0.0.1 .**

This will take a while as a bunch of libraries and distributions are installed, including the email package and the textract, tesseract and ImageMagick distributions.

2. Run docker container  
Start the container by running **docker run -it -p 6969:6969 -v /local/folder/with/emails/:/mnt/my_email_data eml_text_extraction:0.0.1**

This code starts up the container and makes jupyter availible through the browser at your local host. Docker should return the adress to type into your browser.

# Extracting text from eml-files
You simply start up the example [Jupyter Notebook](https://github.com/esbeneickhardt/emlTextExtraction/tree/master/notebook) and it illustrates how things work.
