
#===-------------------------------------------------------------------------------------------===//
# buildslave
#===-------------------------------------------------------------------------------------------===//

FROM ericwf/llvm:9.x AS llvm-tot
FROM ericwf/gcc:9.2.0 as gcc-tot

FROM debian AS runner

RUN apt-get update && \
    apt-get install -y \
      ca-certificates \
      gnupg \
      build-essential \
      wget \
      subversion \
      unzip \
      automake \
      python \
      cmake \
      ninja-build \
      curl \
      git \
      gcc-multilib \
      g++-multilib \
      libc6-dev \
      bison \
      flex \
      libtool \
      autoconf \
      binutils-dev \
      binutils-gold \
      software-properties-common \
      gnupg \
      apt-transport-https \
      sudo \
      bash-completion \
      vim \
      gnupg-agent \
      fish \
      fish-common \
      jq \
      apt-utils \
      systemd \
      systemd-sysv \
      python3 \
      python3-pip \
      python3-dev \
      python3-requests \
      python3-psutil \
      python-psutil \
      php-cli \
      php-dev \
      php-common \
      php-curl \
      docker-compose \
      docker.io \
      make libssl-dev libghc-zlib-dev libcurl4-gnutls-dev libexpat1-dev gettext unzip \
       && \
  rm -rf /var/lib/apt/lists/*

RUN mkdir /arc-install && cd /arc-install && \
    git clone https://github.com/phacility/libphutil.git && \
    git clone https://github.com/phacility/arcanist.git
ENV PATH="$PATH:/arc-install/arcanist/bin"
RUN echo "export PATH=$PATH:/arc-install/arcanist/bin" >> /tmp/arc-path.sh && sudo mv /tmp/arc-path.sh /etc/profile.d/
RUN echo "export PATH=$PATH:/arc-install/arcanist/bin" >> ~/.profile
RUN arc upgrade --

RUN adduser --home=/home/actions-runner --shell /bin/bash --ingroup sudo --disabled-password actions-runner
RUN usermod -aG sudo actions-runner
RUN usermod -aG docker actions-runner

RUN echo "" >> /etc/sudoers
RUN echo "actions-runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY --from=gcc-tot /compiler /opt/gcc-tot
COPY --from=llvm-tot /compiler /opt/llvm-tot
RUN ln -s /opt/llvm-tot/bin/clang /usr/local/bin/ && ln -s /opt/llvm-tot/bin/clang++ /usr/local/bin/
RUN ln -s /opt/gcc-tot/bin/gcc /usr/local/bin/ && ln -s /opt/gcc-tot/bin/g++ /usr/local/bin

RUN echo "export PATH=/opt/llvm-tot/bin:/opt/gcc-tot/bin:$PATH" >> /etc/profile.d/compiler-paths.sh \
  && chmod +x /etc/profile.d/compiler-paths.sh



USER actions-runner
WORKDIR /home/actions-runner/

RUN mkdir /home/actions-runner/arc-install/


ADD ./utils/ /github-utils/
RUN sudo chown -R actions-runner /github-utils/
ADD images/github-actions-runner/register-builder.sh /register-builder.sh
ADD images/github-actions-runner/entrypoint.sh /entrypoint.sh
RUN git --version

