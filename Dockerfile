FROM debian:8.2
MAINTAINER FOSSEE <pythonsupport@fossee.in>

# Update Packages and Install Python & net-tools
RUN apt-get update && apt-get install -y python net-tools git python-pip

# Copy the project folder from host into container
#COPY ./yaksh /src/yaksh

RUN pip install tornado

# Run Yaksh code server
#CMD ["python", "-m", "yaksh.code_server"]

# clone project folder
RUN git clone https://github.com/FOSSEE/online_test.git /src/online_test/

WORKDIR /src/online_test/

# go to yaksh dir
#RUN cd /src/online_test/yaksh

# Run Yaksh code server
#CMD ["python", "-m", "yaksh.code_server"]
