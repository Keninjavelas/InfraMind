# Dockerfile demo showing basic security vulnerabilities
# MEDIUM: latest base image used
FROM ubuntu:latest

# Run as root user
# HIGH: Dockerfile executes as root user
USER root

# Expose port 22 for SSH
# HIGH: Dockerfile exposes port 22 (SSH)
EXPOSE 22

# Install minimal packages (simulated)
RUN apt-get update && apt-get install -y openssh-server

# Startup command
CMD ["/usr/sbin/sshd", "-D"]
