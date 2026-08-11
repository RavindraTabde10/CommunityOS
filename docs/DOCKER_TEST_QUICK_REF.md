# Docker Test & Deploy Quick Reference

## Quick Start (TL;DR)

```bash
# 1. Create test environment file
cp backend/.env.example backend/.env.prod.test

# 2. Run test suite (Linux/macOS)
bash docker-test-prod.sh

# Or Windows
docker-test-prod.bat

# 3. Check results - should see:
#   ✓ Passed:   25+
#   ✗ Failed:   0
#   ⚠ Warnings: 0-2

# 4. If all pass, deploy to EC2
# (see EC2 Deployment section below)
```

---

## Test Suite Commands

### Linux/macOS
```bash
# Make executable (first time only)
chmod +x docker-test-prod.sh

# Run tests (containers keep running)
./docker-test-prod.sh

# Run tests + auto-cleanup
./docker-test-prod.sh --cleanup

# Run with debug output
bash -x docker-test-prod.sh
```

### Windows (PowerShell or Command Prompt)
```cmd
# Run tests
docker-test-prod.bat

# Auto-cleans up after completion
```

---

## What Gets Tested

| Category | Tests | Status |
|----------|-------|--------|
| Prerequisites | Docker installed, compose file exists | ✓ |
| Build | Backend + frontend images build | ✓ |
| Health Checks | Both containers report "healthy" | ✓ |
| Endpoints | API & frontend accessible on correct ports | ✓ |
| Networking | Services can communicate internally | ✓ |
| Volumes | backend_data mounted and writable | ✓ |
| Resources | Memory/CPU limits applied | ✓ |
| Environment | Config loaded from .env file | ✓ |

---

## Expected Output

### All Tests Pass ✅
```
✓ Passed:   25
✗ Failed:   0
⚠ Warnings: 1

════════════════════════════════════════════════════════════════
All tests passed! Safe to deploy to EC2.
════════════════════════════════════════════════════════════════
```
**Action**: Safe to deploy to production

### Some Tests Failed ❌
```
✓ Passed:   20
✗ Failed:   2
⚠ Warnings: 1

════════════════════════════════════════════════════════════════
Some tests failed. Review errors above before deploying.
════════════════════════════════════════════════════════════════
```
**Action**: Fix failures before deploying
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
```

---

## Common Failures & Quick Fixes

### ❌ "Backend Swagger UI not accessible"
```bash
# Check if running and healthy
docker compose -f docker-compose.prod.yml ps backend

# View error logs
docker compose -f docker-compose.prod.yml logs backend | tail -50
```

### ❌ "Frontend HTML check failed"
```bash
# Check nginx logs
docker compose -f docker-compose.prod.yml logs frontend

# Rebuild frontend
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml restart frontend
```

### ❌ "communityos-network not found"
```bash
# Restart services (creates network automatically)
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### ⚠️ "Backend health check may have timed out"
```bash
# Increase startup time in script:
# STARTUP_WAIT=30  (change from 20)

# Re-run test
./docker-test-prod.sh --cleanup
```

---

## Manual Testing (No Script)

```bash
# Start containers
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend

# Test endpoints
curl http://localhost:8000/api/docs        # Backend
curl http://localhost:8080/                # Frontend (test port)

# Stop containers
docker compose -f docker-compose.prod.yml down
```

---

## Pre-Deploy Checklist

Before EC2 deployment, verify:

```
Docker Tests:
  ☑ ./docker-test-prod.sh passes (exit code 0)
  ☑ No failed tests (red ✗)
  ☑ Warnings reviewed and addressed

Environment:
  ☑ backend/.env configured with production values
  ☑ DATABASE_URL points to production DB
  ☑ AWS_S3_BUCKET and credentials set
  ☑ RESEND_API_KEY or email config set
  ☑ SECRET_KEY is strong
  ☑ ENVIRONMENT=production

EC2 Setup:
  ☑ EC2 instance running (Docker + Docker Compose)
  ☑ Security group allows port 80 inbound
  ☑ docker-compose.prod.yml copied to EC2
  ☑ backend/.env set up on EC2

Database:
  ☑ PostgreSQL ready (Supabase/RDS)
  ☑ Database URL configured in .env
  ☑ Migrations can run: alembic upgrade head
```

---

## EC2 Deployment (5 minutes)

```bash
# 1. SSH to EC2
ssh -i key.pem ec2-user@<EC2-IP>

# 2. Clone or copy repo
git clone <repo> /opt/communityos
cd /opt/communityos

# 3. Create production .env
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql://user:pass@db.host/db
SECRET_KEY=your-secret-key-change-this
AWS_S3_BUCKET=your-bucket
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
RESEND_API_KEY=xxx
ENVIRONMENT=production
EOF

# 4. Deploy
docker compose -f docker-compose.prod.yml up --build -d

# 5. Verify
docker compose -f docker-compose.prod.yml ps
docker logs communityos-backend --tail 20

# 6. Access
# http://<EC2-IP>/              → Frontend
# http://<EC2-IP>:8000/api/docs → Backend Swagger
```

---

## Cleanup

```bash
# Stop containers
docker compose -f docker-compose.prod.yml down

# Stop + remove volumes (CAUTION: deletes data)
docker compose -f docker-compose.prod.yml down -v

# Remove test .env
rm backend/.env.prod.test

# Remove test containers (if leftover)
docker compose -f docker-compose.prod.yml down --remove-orphans
```

---

## File Reference

| File | Purpose |
|------|---------|
| `docker-test-prod.sh` | Main test script (Linux/macOS) |
| `docker-test-prod.bat` | Main test script (Windows) |
| `docker-compose.prod.yml` | Production configuration |
| `docker-compose.dev.yml` | Development configuration |
| `docker-compose.yml` | Default (balanced) configuration |
| `DOCKER.md` | Full Docker documentation |
| `DOCKER_TEST_README.md` | Detailed test guide |
| `backend/.env.prod.test` | Test environment (copy from .example) |

---

## Exit Codes

```
0 = Tests passed; safe to deploy
1 = Tests failed; do not deploy
```

Check with:
```bash
./docker-test-prod.sh
echo $?  # 0 or 1
```

---

## Performance

| Phase | Time | Notes |
|-------|------|-------|
| Prerequisites | ~1s | Check tools |
| Build | ~60s | Backend + frontend |
| Startup | ~30s | Services start |
| Health | ~5s | HEALTHCHECK |
| Endpoints | ~10s | API tests |
| Resources | ~3s | Memory/CPU |
| Networking | ~5s | Inter-container |
| Cleanup | ~5s | Stop containers |
| **Total** | **~2 minutes** | Single run |

---

## Support

**Issue**: Script won't run
```bash
# Make executable
chmod +x docker-test-prod.sh

# Or run explicitly
bash docker-test-prod.sh
```

**Issue**: Docker daemon not responding
```bash
# Restart Docker
sudo systemctl restart docker    # Linux
open -a Docker                   # macOS
# Windows: Restart Docker Desktop
```

**Issue**: Port already in use
```bash
# Kill process on port
lsof -i :8080        # Find process
kill -9 <PID>        # Kill it
# Or modify docker-compose.prod.yml ports
```

**Issue**: Container exits immediately
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend
# Look for environment, permission, or startup errors
```

---

## Additional Resources

- **DOCKER.md** — Full documentation (architecture, best practices, troubleshooting)
- **docker-compose.prod.yml** — Production configuration (resource limits, health checks)
- **docker-compose.dev.yml** — Development configuration (hot reload)

---

**Version**: 1.0  
**Last Updated**: 2026-08-11  
**Platforms**: Linux, macOS, Windows 10/11
