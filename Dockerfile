# Dockerfile for M2ARM Development Environment

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV GO_VERSION=1.21.5
ENV PYTHON_VERSION=3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    qemu-user-static \
    qemu-system-arm \
    git \
    curl \
    wget \
    unzip \
    python3 \
    python3-pip \
    python3-venv \
    pkg-config \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Go
RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz \
    && rm go${GO_VERSION}.linux-amd64.tar.gz

# Set up Go environment
ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPATH="/go"
ENV PATH="${GOPATH}/bin:${PATH}"

# Create workspace directory
WORKDIR /workspace

# Copy project files
COPY . .

# Install Python dependencies
RUN cd sdk && \
    python3 -m pip install --upgrade pip && \
    pip3 install -e . && \
    pip3 install pytest pytest-cov flake8 black mypy

# Build Go CLI
RUN cd cli && \
    go mod download && \
    go build -o /usr/local/bin/m2arm main.go

# Set up development environment
RUN mkdir -p /workspace/examples /workspace/output

# Expose common ports for development
EXPOSE 8080 3000

# Default command
CMD ["/bin/bash"]

# Multi-stage build for production
FROM ubuntu:22.04 as production

RUN apt-get update && apt-get install -y \
    qemu-user-static \
    qemu-system-arm \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy built CLI and SDK
COPY --from=0 /usr/local/bin/m2arm /usr/local/bin/m2arm
COPY --from=0 /workspace/sdk /opt/m2arm/sdk

# Install SDK in production
RUN cd /opt/m2arm/sdk && \
    python3 -m pip install --upgrade pip && \
    pip3 install -e .

WORKDIR /workspace

CMD ["m2arm", "--help"]
