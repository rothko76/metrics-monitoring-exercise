FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y stress openssh-server sudo && \
    mkdir /var/run/sshd

# Add a user for SSH
RUN useradd -m devops && echo "devops:devops" | chpasswd && adduser devops sudo

# Allow passwordless SSH login for simplicity (dev/test only)
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
