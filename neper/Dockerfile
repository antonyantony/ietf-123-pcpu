FROM debian:bookworm

RUN echo "deb http://deb.debian.org/debian/ bookworm main" >> /etc/apt/sources.list && \
  echo "deb-src http://deb.debian.org/debian/ bookworm main" >> /etc/apt/sources.list

# Install build deps
RUN apt-get update && apt-get install -y build-essential git

RUN git clone https://github.com/google/neper.git
WORKDIR neper

# Install build script that build.sh will invoke
COPY build-neper.sh .
