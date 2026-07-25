# Based on vaultwarden Dockerfile

# e.g., almalinux:9
ARG base_image
# Toolchain is pulled through rustup: the rust-toolset stream shipped in the
# AlmaLinux AppStream lags behind what recent vaultwarden releases require.
ARG rust_version=1.89.0

FROM ${base_image} AS build

# EL-based builds support multidb
ARG DB=sqlite,mysql,postgresql
ARG rust_version

ENV LANG=C.UTF-8 \
    TZ=UTC \
    TERM=xterm-256color \
    CARGO_HOME="/root/.cargo" \
    RUSTUP_HOME="/root/.rustup" \
    PATH="/root/.cargo/bin:${PATH}" \
    USER="root"

# Install build tooling, DB client libraries and the rpm build stack
RUN dnf -y install \
        gcc \
        gcc-c++ \
        make \
        pkgconf-pkg-config \
        openssl-devel \
        mariadb-connector-c-devel \
        libpq-devel \
        rpm-build \
        systemd-rpm-macros \
        git \
        tar \
        gzip \
        wget \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# mysqlclient-sys looks for mysql_config; the EL connector package installs it
# as mariadb_config only on some releases.
RUN [ -e /usr/bin/mysql_config ] || ln -s mariadb_config /usr/bin/mysql_config

# Install the pinned Rust toolchain, minimal profile, no rust docs
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
      | sh -s -- -y --profile minimal --default-toolchain ${rust_version}

WORKDIR /app

# Copies the complete project
# To avoid copying unneeded files, use .dockerignore
COPY . .
RUN tar -xzv --strip-component=1 -f vaultwarden.tar.gz

# Make sure that we actually build the project
RUN touch src/main.rs

# Build the project
RUN cargo build --features ${DB} --release

# Build the rpm package
RUN make rpm RPM_OUTPUT_DIR=/out
