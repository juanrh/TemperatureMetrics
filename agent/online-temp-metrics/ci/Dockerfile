# https://github.com/conan-io/conan-docker-tools
FROM conanio/gcc10-armv7hf
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt
# This is Ubuntu 20.04 focal https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04
RUN sudo apt-get update
RUN sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
RUN sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
RUN sudo apt-get update
RUN apt-cache policy docker-ce
RUN sudo apt-get install -y docker-ce
RUN sudo apt-get install -y cppcheck
RUN sudo apt-get install -y clang-tools
# https://stackoverflow.com/questions/12578499/how-to-install-boost-on-ubuntu
RUN sudo apt-get install -y libboost-all-dev
WORKDIR /home/conan/project
