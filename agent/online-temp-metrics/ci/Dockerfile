FROM conanio/gcc7
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt
# This is Ubuntu 17.10 Artful: https://gist.github.com/levsthings/0a49bfe20b25eeadd61ff0e204f50088
RUN sudo apt-get update
RUN sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
RUN sudo apt-key fingerprint 0EBFCD88
RUN sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu zesty stable"
RUN sudo apt-get update
RUN sudo apt-get install -y docker-ce
RUN sudo apt-get install -y cppcheck
WORKDIR /home/conan/project
