# Using Ubuntu runtime as parent image
FROM ubuntu:18.04

# Uncommenting sources for apt
RUN sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list

# Installing python
RUN apt update --fix-missing
RUN apt install -y python3
RUN apt install -y python3-pip

# Installing wget
RUN apt install -y wget

# Installing simple editor, curl and pdftotext
RUN apt install -y nano
RUN apt install -y curl
RUN apt install -y build-essential libpoppler-cpp-dev pkg-config python-dev --fix-missing

# Installing local language
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen da_DK.UTF-8
RUN dpkg-reconfigure locales
RUN sed -i -e 's/# da_DK.UTF-8 UTF-8/da_DK.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG da_DK.UTF-8  
ENV LANGUAGE da_DK:da  
ENV LC_ALL da_DK.UTF-8  

# Installing time zone manager
RUN export DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN apt-get update && apt-get install tzdata --fix-missing
RUN dpkg-reconfigure --frontend noninteractive tzdata

# Creating workspace for my app
WORKDIR /emlTextExtraction

# Copying code etc. into workspace
COPY . /emlTextExtraction

# Copying example notebook
RUN mkdir -p /mnt/notebooks
COPY ./notebook/* /mnt/notebooks/

# Installing prerequisites for textract
RUN apt update --fix-missing
RUN apt-get install -y libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext tesseract-ocr flac ffmpeg 
RUN apt-get install -y lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev tesseract-ocr-dan 
RUN apt-get install -y libxml2-dev libxslt1-dev antiword poppler-utils zlib1g-dev

# Installing python packages from requirements.txt
RUN pip3 install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Installing textract
RUN cd libraries_python && tar xf textract-1.6.3.tar.gz && cd textract-1.6.3 && python3 setup.py install && cd .. && rm -r textract-1.6.3

# Installing imagemagick
RUN apt -y build-dep imagemagick
RUN cd libraries_debian && tar xf ImageMagick.tar.gz && cd ImageMagick-7* && ./configure && make && make install && ldconfig /usr/local/lib && cd .. && rm -r ImageMagick-7*

# Run app when container starts
EXPOSE 6969
CMD jupyter notebook --ip 0.0.0.0 --no-browser --allow-root --port=6969 --notebook-dir='/mnt/notebooks'