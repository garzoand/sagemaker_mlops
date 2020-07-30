# This is the Dockerfile, which defines how our container can be built. 
# ...
#

FROM ubuntu:18.04

# Installing python3, nginx and some other tools needed to run and serve our ML model
RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         python \
         nginx \
         ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Here we get all python packages.
# There's substantial overlap between scipy and numpy that we eliminate by
# linking them together. Likewise, pip leaves the install caches populated which uses
# a significant amount of space. These optimizations save a fair amount of space in the
# image, which reduces start up time.
RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && \
    pip install numpy==1.16.6 scipy==1.2.3 xgboost==0.82 pandas flask gevent gunicorn && \
        (cd /usr/local/lib/python2.7/dist-packages/scipy/.libs; rm *; ln ../../numpy/.libs/* .) && \
        rm -rf /root/.cache

# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

COPY model_code /opt/program

# Disable buffering the standard output stream. This means that logs can be delivered to the user quickly
ENV PYTHONUNBUFFERED=TRUE
# Disabling writing down .pyc files which are not needed
ENV PYTHONDONTWRITEBYTECODE=TRUE
# We copied our scripts to the container under the /opt/program folder. Now we add this folder to the path
# allowing the users to be able to call the "serve" and "train" scripts without explicitly defining
# their locations
ENV PATH="/opt/program:${PATH}"

WORKDIR /opt/program
