ARG DOCKER_BASE_IMAGE
FROM $DOCKER_BASE_IMAGE

ARG VCS_REF
ARG BUILD_DATE
LABEL \
    maintainer="https://ocr-d.de/en/contact" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/kba/page-to-alto" \
    org.label-schema.build-date=$BUILD_DATE \
    org.opencontainers.image.vendor="DFG-Funded Initiative for Optical Character Recognition Development" \
    org.opencontainers.image.title="page-to-alto" \
    org.opencontainers.image.description="Convert PAGE (v. 2019) to ALTO (v. 2.0 - 4.2)" \
    org.opencontainers.image.source="https://github.com/kba/page-to-alto" \
    org.opencontainers.image.documentation="https://github.com/kba/page-to-alto/blob/${VCS_REF}/README.md" \
    org.opencontainers.image.revision=$VCS_REF \
    org.opencontainers.image.created=$BUILD_DATE \
    org.opencontainers.image.base.name=ocrd/core

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONIOENCODING=utf8
ENV XDG_DATA_HOME=/usr/local/share
ENV XDG_CONFIG_HOME /usr/local/share/ocrd-resources

WORKDIR /build/p2a
COPY src/ ./src
COPY pyproject.toml .
COPY ocrd-tool.json .
COPY requirements.txt .
COPY README.md .
COPY Makefile .
# prepackage ocrd-tool.json as ocrd-all-tool.json
RUN ocrd ocrd-tool ocrd-tool.json dump-tools > $(dirname $(ocrd bashlib filename))/ocrd-all-tool.json
# install everything and reduce image size
RUN make install && rm -fr /build/p2a
# smoke test
RUN page-to-alto -h
RUN ocrd-page2alto-transform -h

WORKDIR /data
VOLUME /data
