

# Docker image for wrk: wrk is a modern HTTP benchmarking tool capable of generating significant
#  load when run on a single multi-core CPU. It combines a multithreaded design with scalable event notification
#  systems such as epoll and kqueue.
# SEE https://github.com/wg/wrk
# From https://github.com/skandyla/docker-wrk/blob/master/ubuntu16.04/Dockerfile
FROM       ubuntu:16.04

RUN echo "===> Installing  tools..."  && \
  apt-get -y update && \
  apt-get -y install build-essential curl && \
  \
  echo "===> Installing wrk" && \
  WRK_VERSION=$(curl -L https://github.com/wg/wrk/raw/master/CHANGES 2>/dev/null | \
  egrep '^wrk' | head -n 1 | awk '{print $2}') && \
  echo $WRK_VERSION  && \
  mkdir /opt/wrk && \
  cd /opt/wrk && \
  curl -L https://github.com/wg/wrk/archive/$WRK_VERSION.tar.gz | \
  tar zx --strip 1 && \
  make && \
  cp wrk /usr/local/bin/ && \
  \
  echo "===> Cleaning the system" && \
  apt-get -f -y --auto-remove remove build-essential curl && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /opt/wrk/

WORKDIR /data
ENTRYPOINT ["wrk"]
CMD ["--help"]
