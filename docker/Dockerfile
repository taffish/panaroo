# syntax=docker/dockerfile:1.7

ARG DEBIAN_IMAGE=debian:trixie-slim@sha256:3a39a0592364683e6bab97937b72cad5a8fa6dcbbee90edb3bb48c7f8e94f258
FROM ${DEBIAN_IMAGE} AS builder

ARG TARGETARCH
ARG PANAROO_VERSION=1.8.1
ARG PANAROO_SHA256=b909740a0e7ab371a871a18467f1eaa61d5d0581117c62f440bd16c16b37c302
ARG BIOCODE_VERSION=0.12.1
ARG BIOCODE_SHA256=cfc6d19948bbfd525c8d46739c2a6ffc8d5aae8c4e7f7cd9ac9ed2de30a702fd
ARG TAXADB_VERSION=0.12.1
ARG TAXADB_SHA256=cdfe000e474eb56d2174349fa40b2eacb6801687a748349c10e7db06a4247a3b
ARG PROKKA_VERSION=1.14.6
ARG PROKKA_SHA256=f730b5400ea9e507bfe6c5f3d22ce61960a897195c11571c2e1308ce2533faf8
ARG FAMSA_VERSION=2.4.1
ARG FAMSA_AMD64_SHA256=fe3a8813f6c68d69552f3713820ec11b730dba0cc18c837c72c8659d8bbe8438
ARG FAMSA_ARM64_SHA256=583c577e25dd111e870f49e7ef9bc46c2a7a010e81d844b354ba23b422d6ed79
ARG MUSCLE_VERSION=5.3
ARG MUSCLE_SHA256=74b22a94e630b16015c2bd9ae83aa2be2c2048d3e41f560b2d4a954725c81968
ARG VCXPROJ_MAKE_SHA256=902735703004c47705ffa389329378f237fecb154945b489edf6abe260c6694f

ENV DEBIAN_FRONTEND=noninteractive

# Debian repositories are rolling within this suite: dependency versions and
# availability can drift. The base digest does not freeze future apt results.
# On failure, distinguish network/TLS/index errors from 404 retirement,
# truncated downloads and changed bytes; check the official release and platform.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get -o Acquire::Retries=10 update \
 && apt-get -o Acquire::Retries=10 install -y --no-install-recommends ca-certificates \
 && sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
 && apt-get -o Acquire::Retries=10 update \
 && apt-get -o Acquire::Retries=10 install -y --no-install-recommends \
      curl \
      g++ \
      gzip \
      make \
      python3 \
      python3-pip \
      python3-venv \
      tar

# Fixed archives fail closed on checksum changes. Their upstream hosts can
# withdraw files; hashes ensure identity, not permanent download availability.
# pip build-isolation dependencies may also change independently of these pins.
# Restore old archives only from trusted copies matching the original SHA256.
# Otherwise review new official versions, architectures, dependencies and licenses
# before updating source identity and rerunning native builds, offline smoke and
# wrapper checks. Do not bypass integrity checks or blindly regenerate hashes.
RUN set -eux; \
    mkdir -p /opt/panaroo/libexec /opt/panaroo/prokka-bin /opt/panaroo/share/licenses /opt/panaroo/share/provenance; \
    curl -fsSL "https://codeload.github.com/gtonkinhill/panaroo/tar.gz/refs/tags/v${PANAROO_VERSION}" -o /tmp/panaroo.tar.gz; \
    echo "${PANAROO_SHA256}  /tmp/panaroo.tar.gz" | sha256sum -c -; \
    tar -xzf /tmp/panaroo.tar.gz -C /tmp; \
    cp "/tmp/panaroo-${PANAROO_VERSION}/LICENSE" /opt/panaroo/share/licenses/PANAROO-LICENSE; \
    install -m 0644 "/tmp/panaroo-${PANAROO_VERSION}/scripts/convert_bakta_to_prokka_gff.py" /opt/panaroo/libexec/convert_bakta_to_prokka_gff.py; \
    curl -fsSL "https://files.pythonhosted.org/packages/09/89/0d0e898d641e714089c8f99b4255fa7cd62836190f7ac03d18aa8bf09afb/biocode-${BIOCODE_VERSION}.tar.gz" -o "/tmp/biocode-${BIOCODE_VERSION}.tar.gz"; \
    echo "${BIOCODE_SHA256}  /tmp/biocode-${BIOCODE_VERSION}.tar.gz" | sha256sum -c -; \
    tar -xzf "/tmp/biocode-${BIOCODE_VERSION}.tar.gz" -C /tmp; \
    cp "/tmp/biocode-${BIOCODE_VERSION}/LICENSE" /opt/panaroo/share/licenses/BIOCODE-LICENSE; \
    curl -fsSL "https://files.pythonhosted.org/packages/ea/f8/b29e362cf7e174d79deb3df244cceb71c975e98c3e15572fb7ee44d5fe49/taxadb-${TAXADB_VERSION}-py3-none-any.whl" -o "/tmp/taxadb-${TAXADB_VERSION}-py3-none-any.whl"; \
    echo "${TAXADB_SHA256}  /tmp/taxadb-${TAXADB_VERSION}-py3-none-any.whl" | sha256sum -c -; \
    curl -fsSL "https://codeload.github.com/tseemann/prokka/tar.gz/refs/tags/v${PROKKA_VERSION}" -o /tmp/prokka.tar.gz; \
    echo "${PROKKA_SHA256}  /tmp/prokka.tar.gz" | sha256sum -c -; \
    tar -xzf /tmp/prokka.tar.gz -C /tmp; \
    cp -a "/tmp/prokka-${PROKKA_VERSION}/db" /opt/panaroo/share/prokka-db; \
    for command in "/tmp/prokka-${PROKKA_VERSION}"/bin/prokka*; do \
      install -m 0755 "$command" "/opt/panaroo/prokka-bin/${command##*/}"; \
    done; \
    install -m 0755 "/tmp/prokka-${PROKKA_VERSION}/binaries/common/minced" /opt/panaroo/prokka-bin/minced; \
    install -m 0644 "/tmp/prokka-${PROKKA_VERSION}/binaries/common/minced.jar" /opt/panaroo/prokka-bin/minced.jar; \
    cp "/tmp/prokka-${PROKKA_VERSION}"/doc/LICENSE.* /opt/panaroo/share/licenses/; \
    python3 -m venv --system-site-packages /opt/panaroo/venv; \
    /opt/panaroo/venv/bin/pip install --no-cache-dir --no-deps "/tmp/taxadb-${TAXADB_VERSION}-py3-none-any.whl" "/tmp/biocode-${BIOCODE_VERSION}.tar.gz" "/tmp/panaroo-${PANAROO_VERSION}"; \
    find /opt/panaroo/venv/bin -maxdepth 1 -type f \
      ! -name 'panaroo*' ! -name 'run_prokka' -delete; \
    find /opt/panaroo/venv -type f -name '*.py[co]' -delete; \
    find /opt/panaroo/venv -depth -type d -name __pycache__ -empty -delete; \
    printf '%s\n' \
      "panaroo_version=${PANAROO_VERSION}" \
      "panaroo_commit=dbe596c3d24acfe2df1be64f76550b324d167243" \
      "panaroo_source_sha256=${PANAROO_SHA256}" \
      "biocode_version=${BIOCODE_VERSION}" \
      "biocode_source_sha256=${BIOCODE_SHA256}" \
      "taxadb_version=${TAXADB_VERSION}" \
      "taxadb_wheel_sha256=${TAXADB_SHA256}" \
      "prokka_version=${PROKKA_VERSION}" \
      "prokka_source_sha256=${PROKKA_SHA256}" \
      > /opt/panaroo/share/provenance/source.txt

RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64) famsa_arch=x64; famsa_sha="${FAMSA_AMD64_SHA256}" ;; \
      arm64) famsa_arch=arm64; famsa_sha="${FAMSA_ARM64_SHA256}" ;; \
      *) echo "unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -fsSL "https://github.com/refresh-bio/FAMSA/releases/download/v${FAMSA_VERSION}/famsa-v${FAMSA_VERSION}-${famsa_arch}_linux.tar.gz" -o /tmp/famsa.tar.gz; \
    echo "${famsa_sha}  /tmp/famsa.tar.gz" | sha256sum -c -; \
    mkdir -p /tmp/famsa; \
    tar -xzf /tmp/famsa.tar.gz -C /tmp/famsa; \
    install -m 0755 /tmp/famsa/famsa /opt/panaroo/famsa; \
    cp /tmp/famsa/LICENSE /opt/panaroo/share/licenses/FAMSA-LICENSE; \
    printf '%s\n' \
      "famsa_version=${FAMSA_VERSION}" \
      "famsa_asset_arch=${famsa_arch}" \
      "famsa_asset_sha256=${famsa_sha}" \
      >> /opt/panaroo/share/provenance/source.txt

RUN set -eux; \
    curl -fsSL "https://codeload.github.com/rcedgar/muscle/tar.gz/refs/tags/v${MUSCLE_VERSION}" -o /tmp/muscle.tar.gz; \
    echo "${MUSCLE_SHA256}  /tmp/muscle.tar.gz" | sha256sum -c -; \
    tar -xzf /tmp/muscle.tar.gz -C /tmp; \
    cp "/tmp/muscle-${MUSCLE_VERSION}/LICENSE" /opt/panaroo/share/licenses/MUSCLE-LICENSE; \
    curl -fsSL "https://raw.githubusercontent.com/rcedgar/vcxproj_make/806d016/vcxproj_make.py" -o "/tmp/muscle-${MUSCLE_VERSION}/src/vcxproj_make.py"; \
    echo "${VCXPROJ_MAKE_SHA256}  /tmp/muscle-${MUSCLE_VERSION}/src/vcxproj_make.py" | sha256sum -c -; \
    sed -i 's/defined(__arm64__)/defined(__arm64__) || defined(__aarch64__)/' "/tmp/muscle-${MUSCLE_VERSION}/src/myutils.h"; \
    sed -i 's/ -march=native//g' "/tmp/muscle-${MUSCLE_VERSION}/src/vcxproj_make.py"; \
    cd "/tmp/muscle-${MUSCLE_VERSION}/src"; \
    python3 ./vcxproj_make.py --openmp; \
    install -m 0755 ../bin/muscle /opt/panaroo/muscle; \
    printf '%s\n' \
      "muscle_version=${MUSCLE_VERSION}" \
      "muscle_source_sha256=${MUSCLE_SHA256}" \
      "muscle_vcxproj_make_sha256=${VCXPROJ_MAKE_SHA256}" \
      "muscle_aarch64_macro_fix=__aarch64__" \
      "muscle_portable_build=no_march_native" \
      >> /opt/panaroo/share/provenance/source.txt

FROM ${DEBIAN_IMAGE}

ARG PANAROO_VERSION=1.8.1

LABEL org.opencontainers.image.title="TAFFISH Panaroo" \
      org.opencontainers.image.description="Panaroo bacterial pangenome analysis with its supported external tools" \
      org.opencontainers.image.source="https://github.com/taffish/panaroo" \
      org.opencontainers.image.version="${PANAROO_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV DEBIAN_FRONTEND=noninteractive \
    MPLBACKEND=Agg \
    PROKKA_DBDIR=/opt/panaroo/share/prokka-db \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/opt/panaroo/venv/bin:/usr/local/bin:/usr/bin:/bin \
    TAFFISH_ENV=TAFFISH \
    TAFFISH_NAME=panaroo \
    TAFFISH_VERSION=${PANAROO_VERSION} \
    TAFFISH_RELEASE=1

# Runtime apt packages can drift; record the resolved versions below. A failed
# future source/dependency fetch requires review, not silently relaxing hashes.
# This resolved package inventory is provenance, not an input dependency lock.
# Headless Java remains required by Prokka's MinCED after the desktop split.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get -o Acquire::Retries=10 update \
 && apt-get -o Acquire::Retries=10 install -y --no-install-recommends ca-certificates \
 && sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
 && apt-get -o Acquire::Retries=10 update \
 && apt-get -o Acquire::Retries=10 install -y --no-install-recommends \
      bash \
      aragorn \
      barrnap \
      cd-hit \
      clustalo \
      default-jre-headless \
      dpkg-dev \
      hmmer \
      infernal \
      less \
      libbio-perl-perl \
      libbio-searchio-hmmer-perl \
      libswiss-perl \
      libxml-simple-perl \
      mafft \
      mash \
      ncbi-blast+ \
      ncbi-tools-bin \
      parallel \
      prank \
      prodigal \
      python3 \
      python3-biopython \
      python3-dendropy \
      python3-edlib \
      python3-gffutils \
      python3-igraph \
      python3-intbitset \
      python3-jinja2 \
      python3-joblib \
      python3-matplotlib \
      python3-networkx \
      python3-numba \
      python3-numpy \
      python3-peewee \
      python3-plotly \
      python3-requests \
      python3-scipy \
      python3-sklearn \
      python3-tqdm \
 && mkdir -p /opt/panaroo/share/provenance \
 && dpkg-query -W -f='${binary:Package}\t${Version}\n' | sort > /opt/panaroo/share/provenance/debian-packages.tsv \
 && find /usr/share/doc -type f ! -name copyright -delete \
 && find /usr/share/doc -type l -delete \
 && find /usr/share/doc -depth -type d -empty -delete \
 && rm -rf /usr/share/man/* /usr/share/info/* \
 && find /usr -xdev -type f -name '*.py[co]' -delete \
 && find /usr -xdev -depth -type d -name __pycache__ -empty -delete

# MAFFT invokes file for UTF-16/UTF-32 input diagnostics before alignment.
# Keep this runtime addition separate so the scientific stack remains cached.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get -o Acquire::Retries=10 update \
 && apt-get -o Acquire::Retries=10 install -y --no-install-recommends file \
 && dpkg-query -W -f='${binary:Package}\t${Version}\n' | sort > /opt/panaroo/share/provenance/debian-packages.tsv \
 && find /usr/share/doc -type f ! -name copyright -delete \
 && find /usr/share/doc -type l -delete \
 && find /usr/share/doc -depth -type d -empty -delete \
 && rm -rf /usr/share/man/* /usr/share/info/*

ENV PYTHONWARNINGS=ignore::SyntaxWarning

COPY --from=builder /opt/panaroo /opt/panaroo
COPY docker/panaroo-smoke.sh /opt/panaroo/share/testdata/panaroo-smoke.sh
COPY docker/panaroo-smoke-fixtures.py /opt/panaroo/share/testdata/panaroo-smoke-fixtures.py
COPY docker/panaroo-convert-bakta-to-prokka-gff /usr/local/bin/panaroo-convert-bakta-to-prokka-gff
COPY src/mash_resources.py /opt/panaroo/libexec/mash_resources.py

RUN set -eux; \
    chmod 0755 /opt /opt/panaroo /opt/panaroo/share /opt/panaroo/share/testdata; \
    chmod 0755 /opt/panaroo/libexec/mash_resources.py; \
    ln -s /opt/panaroo/libexec/mash_resources.py /usr/local/bin/panaroo-mash-resources; \
    ln -s /opt/panaroo/famsa /usr/local/bin/famsa; \
    ln -s /opt/panaroo/muscle /usr/local/bin/muscle; \
    for command in /opt/panaroo/prokka-bin/prokka*; do \
      ln -s "$command" "/usr/local/bin/${command##*/}"; \
    done; \
    ln -s /opt/panaroo/prokka-bin/minced /usr/local/bin/minced; \
    chmod 0755 /opt/panaroo/share/testdata/panaroo-smoke.sh /opt/panaroo/share/testdata/panaroo-smoke-fixtures.py /usr/local/bin/panaroo-convert-bakta-to-prokka-gff; \
    ln -s /opt/panaroo/share/testdata/panaroo-smoke.sh /usr/local/bin/panaroo-smoke; \
    prokka --setupdb; \
    sh -x /opt/panaroo/share/testdata/panaroo-smoke.sh identity

WORKDIR /root
