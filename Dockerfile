ARG DOCKER_BASE_IMAGE
FROM $DOCKER_BASE_IMAGE

ARG VCS_REF
ARG BUILD_DATE
LABEL \
    maintainer="https://ocr-d.de/kontakt" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/kba/page-to-alto" \
    org.label-schema.build-date=$BUILD_DATE

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONIOENCODING=utf8
ENV XDG_DATA_HOME=/usr/local/share

WORKDIR /build-p2a
COPY src/ ./src
COPY pyproject.toml .
COPY requirements.txt .
COPY README.md .
COPY Makefile .
RUN make install

WORKDIR /data
VOLUME /data
