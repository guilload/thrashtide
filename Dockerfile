FROM ubuntu:14.04

RUN apt-get -y update
RUN apt-get -y install curl

RUN curl -O https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.3.0-Linux-x86_64.sh
RUN bash Anaconda-2.3.0-Linux-x86_64.sh -b
ENV PATH /root/anaconda/bin:$PATH"

RUN apt-get -y install git
RUN git clone https://github.com/guilload/thrashtide.git
WORKDIR /thrashtide
RUN git checkout develop

RUN conda install --yes --file conda_requirements.txt
RUN pip install -r requirements.txt
RUN python setup.py install

EXPOSE 8000

CMD gunicorn -b 0.0.0.0:8000 -w 2 thrashtide.app:THRASHTIDE
