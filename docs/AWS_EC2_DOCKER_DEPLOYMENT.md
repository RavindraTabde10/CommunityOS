# AWS EC2 Docker Deployment

This guide explains how to deploy the CommunityOS application on an AWS EC2 instance using Docker and Docker Compose.

## Prerequisites

- AWS account with permissions to create EC2 instances and security groups
- AWS CLI installed and configured locally, if using command-line provisioning
- Docker installed on the EC2 instance
- Docker Compose available on the EC2 instance
- SSH access to the EC2 instance

## Recommended EC2 Instance

- Instance type: `t3.small` or `t3.medium`
- OS: Amazon Linux 2023, Ubuntu 24.04 LTS, or similar
- Storage: 20 GB EBS (adjust based on expected data size)

## Security Group Rules

Allow inbound traffic for:

- `22` TCP — SSH
- `80` TCP — HTTP for frontend access
- `8000` TCP — Optional backend access for direct API testing

For production, restrict SSH to known IP addresses and consider using HTTPS via a load balancer or reverse proxy.

## Deployment Steps

### 1. Launch the EC2 Instance

1. Open the AWS EC2 console.
2. Launch a new instance with your chosen Linux distribution.
3. Attach a key pair for SSH access.
4. Configure the security group with the inbound rules above.
5. Launch the instance.

### 2. Connect to the Instance

```bash
ssh -i /path/to/key.pem ec2-user@<EC2_PUBLIC_IP>
```

For Ubuntu, use `ubuntu@<EC2_PUBLIC_IP>`.

### 3. Install Docker

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

On Ubuntu:

```bash
sudo apt update -y
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Log out and log back in if Docker commands require group membership changes.

### 4. Install Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose version
```

### 5. Clone the Repository

```bash
cd /home/ec2-user
git clone https://github.com/<your-repo>/CommunityOS.git
cd CommunityOS
```

Replace the repository URL with the appropriate source.

### 6. Configure Environment

For the backend, create an `.env` file in `backend/` with required settings.

Example minimal `.env`:

```bash
cd backend
cat > .env <<'EOF'
SECRET_KEY=change-me
DATABASE_URL=sqlite:///./data/society_app.db
CORS_ORIGINS=http://localhost:5173
EOF
```

> Note: For production, prefer PostgreSQL or managed database hosting and secure secrets via AWS Secrets Manager.

### 7. Start the Application with Docker Compose

From the repo root:

```bash
docker compose up --build -d
```

This builds and starts both services.

### 8. Verify Deployment

- Frontend: `http://<EC2_PUBLIC_IP>:5173`
- Backend health: `http://<EC2_PUBLIC_IP>:8000/health`
- Backend API docs: `http://<EC2_PUBLIC_IP>:8000/api/docs`

If the frontend does not show the API correctly, confirm that the NGINX proxy in `frontend/nginx.conf` is forwarding `/api` to `http://backend:8000/api/`.

## Optional: Persist Data Between Restarts

Docker volumes are defined in `docker-compose.yml` for backend persistence. To inspect volume usage:

```bash
docker volume ls
docker volume inspect communityos_backend_data
```

## Updating the Deployment

To apply code updates:

```bash
git pull origin main
docker compose build --no-cache
docker compose up -d
```

## Cleanup

To stop and remove the containers:

```bash
docker compose down
```

To remove volumes too:

```bash
docker compose down -v
```

## Notes

- This guide is intended for a simple EC2-based deployment.
- For public production use, add HTTPS support with a reverse proxy or load balancer.
- Use a managed database for production workloads rather than SQLite.
