# Dockerfile may have following Arguments:
# tag - tag for the Base image, (e.g. 2.9.1 for tensorflow)
# branch - user repository branch to clone (default: master, another option: test)
# jlab - if to insall JupyterLab (true) or not (false)
#
# To build the image:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> --build-arg arg=value .
# or using default args:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> .
#
# [!] Note: For the Jenkins CI/CD pipeline, input args are defined inside the
# Jenkinsfile, not here!

ARG tag=3.10-bookworm

# Base image, e.g. tensorflow/tensorflow:2.9.1
FROM python:${tag}

LABEL maintainer='Judith Sáinz-Pardo '
LABEL version='0.0.1'
# Federated learning server with flower

# What user branch to clone [!]
ARG branch=main

# If to install JupyterLab
ARG jlab=true

# Install Ubuntu packages
# - gcc is needed in Pytorch images because deepaas installation might break otherwise (see docs) (it is already installed in tensorflow images)
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    git \
    curl \
    nano \
    tini \     
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.x86_64 && cp ./ttyd.x86_64 /usr/bin/ttyd && chmod +x /usr/bin/ttyd

# Update python packages
# [!] Remember: DEEP API V2 only works with python>=3.6
RUN python3 --version && \
    pip3 install --no-cache-dir --upgrade pip "setuptools<60.0.0" wheel

# TODO: remove setuptools version requirement when [1] is fixed
# [1]: https://github.com/pypa/setuptools/issues/3301

# Set LANG environment
ENV LANG C.UTF-8

# Set the working directory
WORKDIR /srv

# Initialization scripts
RUN git clone --depth 1 https://github.com/deephdc/deep-start /srv/.deep-start && \
    ln -s /srv/.deep-start/deep-start.sh /usr/local/bin/deep-start && \
    ln -s /srv/.deep-start/run_jupyter.sh /usr/local/bin/run_jupyter

# Install JupyterLab
ENV JUPYTER_CONFIG_DIR /srv/.deep-start/

# Necessary for the Jupyter Lab terminal
ENV SHELL /bin/bash
RUN if [ "$jlab" = true ]; then \
    # by default has to work (1.2.0 wrongly required nodejs and npm)
    pip3 install --no-cache-dir jupyterlab ; \
    else echo "[INFO] Skip JupyterLab installation!"; fi

# Install user app
RUN git clone --depth 1 -b $branch https://github.com/deephdc/federated-server && \
    cd  federated-server && \
    pip3 install --no-cache-dir -e . && \
    cd ..

# Open ports: DEEPaaS (5000), Monitoring (6006), Jupyter (8888)
EXPOSE 5000 6006 8888

# Launch deepaas
#CMD ["python3", "-m", "fedserver.server"]

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["ttyd","-p", "6006", "python3", "-m", "fedserver.server"]