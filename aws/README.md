# AWS Deployment Guide

This guide covers deploying the Cman game to AWS EC2 using Docker and Traefik for SSL termination.

## Prerequisites

- AWS EC2 instance (Amazon Linux 2023 recommended)
- Domain name pointing to your EC2 instance
- Security group allowing ports 80 and 443

## SSH Connection

``` sh
# Connect to EC2 instance
ssh -i cman.pem ec2-user@cman.rjchicago.com
```

## Install Docker

``` sh
# Update repos
sudo dnf update -y

# Enable Docker repo
sudo dnf install -y docker

# Start and enable service
sudo systemctl enable docker
sudo systemctl start docker

# Add your user to the docker group
sudo usermod -aG docker ec2-user
```

## Install Docker Compose

``` sh
# install prerequisites
sudo dnf install -y curl

# download the latest stable release (v2.x) for Linux x86_64
sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# make it executable
sudo chmod +x /usr/local/bin/docker-compose

# verify
docker-compose version
```

## Let's Encrypt

``` sh
sudo mkdir -p ./letsencrypt
sudo touch ./letsencrypt/acme.json
sudo chown root:root ./letsencrypt/acme.json
sudo chmod 600 ./letsencrypt/acme.json
```

## Docker Daemon

``` sh
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "5" }
}
EOF
sudo systemctl restart docker
```

## Deployment

1. **Clone or copy your docker-compose.yaml** to the EC2 instance
2. **Update the configuration** in docker-compose.yaml:
   - Change the domain in the Traefik rule
   - Update the email for Let's Encrypt
3. **Start the services**:

``` sh
# Start services in detached mode
docker-compose up -d

# Check logs
docker-compose logs -f

# Check status
docker-compose ps
```

## Maintenance

``` sh
# Update the application
docker-compose pull
docker-compose up -d

# View logs
docker-compose logs cman
docker-compose logs traefik

# Stop services
docker-compose down

# Clean up unused images
docker system prune -f
```

## Troubleshooting

- **SSL Certificate Issues**: Check that your domain DNS is pointing to the correct IP
- **Port Access**: Ensure security group allows inbound traffic on ports 80 and 443
- **Container Issues**: Use `docker-compose logs <service>` to check individual service logs
- **Disk Space**: Monitor with `df -h` and clean up with `docker system prune`
