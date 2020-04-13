
#===-------------------------------------------------------------------------------------------===//
# buildslave
#===-------------------------------------------------------------------------------------------===//

FROM debian:stretch AS base-image

ADD install-packages.sh /tmp/
RUN /tmp/install-packages.sh && rm /tmp/install-packages.sh
RUN apt-get update && apt-get install --no-install-recommends -y gridsite-clients

FROM base-image as worker-image

ADD bundle-packages.sh /
RUN mkdir /packages
VOLUME /packages

