# One Dockerfile for every SSH device: the base image is chosen in docker-compose.lab.yml
ARG BASE_IMAGE=ubuntu:22.04
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive

# Install OpenSSH and generate the host keys.
# We never log in to these machines, we only read their SSH banner.
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd \
    && ssh-keygen -A

EXPOSE 22

# -D: stay in the foreground, -e: write logs to stderr (visible in docker logs)
CMD ["/usr/sbin/sshd", "-D", "-e"]