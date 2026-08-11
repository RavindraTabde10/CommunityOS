# Docker Production Test Suite

Automated test scripts to validate `docker-compose.prod.yml` before deploying to EC2 or production.

## Overview

This test suite validates:

✅ **Container Health** — HEALTHCHECK passes for both backend and frontend  
✅ **API Endpoints** — Backend Swagger UI and frontend accessible  
✅ **Networking** — Services communicate via internal bridge network  
✅ **Volumes** — Persistent storage mounted and writable  
✅ **Resource Limits** — Memory and CPU constraints applied  
✅ **Environment Variables** — Config loaded correctly  
✅ **Service Dependencies** — Frontend waits for backend health  

---

## Scripts

### Linux/macOS: `docker-test-prod.sh`

Comprehensive bash script with colored output and detailed reporting.

**Usage:**
```bash
# Run tests (containers remain running after)
./docker-test-prod.sh

# Run tests and auto-cleanup on completion
./docker-test-prod.sh --cleanup
```

**Requirements:**
- Bash 4.0+
- Docker 25.0+
- Docker Compose 2.20+
- curl (for endpoint tests)
- Standard Unix tools (sed, grep, awk)

**Output:**
- Color-coded results: ✓ (pass), ✗ (fail), ⚠ (warning)
- Detailed test report at end
- Exit code: 0 (all pass), 1 (failures)

---

### Windows: `docker-test-prod.bat`

Batch script for Windows environments.

**Usage:**
```cmd
REM Run tests
docker-test-prod.bat

REM Note: Batch version auto-cleans up after completion
```

**Requirements:**
- Windows 10/11 with Docker Desktop
- Docker Compose 2.20+
- curl (included in Windows 10+)
- PowerShell 3.0+

---

## What Gets Tested

### 1. Prerequisites (Pass/Fail)
- Docker installed and working
- Docker Compose available
- `docker-compose.prod.yml` exists
- Environment file exists or can be created

### 2. Image Build (Pass/Fail)
- Backend image builds successfully
- Frontend image builds successfully
- No build errors or missing dependencies

### 3. Container Startup (Pass/Fail)
- Backend container starts
- Frontend container starts
- Services started within timeout

### 4. Container Health (Pass/Fail)
- Backend HEALTHCHECK: curl `/api/docs` → HTTP 200
- Frontend HEALTHCHECK: wget `/index.html` → HTTP 200
- Both marked as "healthy" in `docker ps`

### 5. API Endpoints (Pass/Fail)
- Backend Swagger UI: `http://localhost:8000/api/docs` → 200
- Backend root: `http://localhost:8000/` → responds
- Frontend: `http://localhost:8080/` → 200 (test port)
- Frontend HTML: loads valid `<html>` or `<!DOCTYPE`

### 6. Resource Limits (Warning/Pass)
- Backend memory limit visible: `docker inspect`
- Frontend memory limit visible: `docker inspect`
- Current usage reported: `docker stats`

### 7. Networking (Pass/Fail)
- `communityos-network` bridge exists
- Backend container has internal IP
- Frontend container has internal IP
- Frontend can reach backend via `http://backend:8000` (internal)

### 8. Volumes (Pass/Fail)
- `backend_data` volume exists
- Backend can write to `/app/data`
- Data persists across restarts

### 9. Environment (Pass/Warning)
- `PYTHONUNBUFFERED=1` set in backend
- `.env` file loaded from `env_file:` directive

---

## Running Tests Locally

### Step 1: Create test environment file

```bash
# Copy example .env to test version
cp backend/.env.example backend/.env.prod.test

# Edit with test values
nano backend/.env.prod.test
```

Or create a minimal one:
```bash
cat > backend/.env.prod.test << EOF
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=test-secret-key-do-not-use-in-production
ENVIRONMENT=test
JWT_EXPIRATION_HOURS=24
EOF
```

### Step 2: Run test script

**Linux/macOS:**
```bash
chmod +x docker-test-prod.sh
./docker-test-prod.sh
```

**Windows (PowerShell):**
```powershell
.\docker-test-prod.bat
```

or Command Prompt:
```cmd
docker-test-prod.bat
```

### Step 3: Review results

The script will output:
```
✓ Passed:   25
✗ Failed:   0
⚠ Warnings: 2

════════════════════════════════════════════════════════════════
All tests passed! Safe to deploy to EC2.
════════════════════════════════════════════════════════════════
```

**Exit code 0**: All tests passed → safe to deploy  
**Exit code 1**: Tests failed → fix issues before deploying

---

## Interpreting Results

### ✓ Pass (Green)
Test succeeded. No action needed.

### ✗ Fail (Red)
**Test failed.** Do NOT deploy to production. Examples:
- Backend health check failed
- Frontend cannot access API endpoint
- Volumes not writable
- Network bridge missing

**Fix**: Check logs and resolve before retesting
```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
```

### ⚠ Warning (Yellow)
**Test had issues but may be recoverable.** Review before deploying. Examples:
- Container still starting during health check
- Resource limits not detected (may use default)
- API proxy failed (may not be expected endpoint)

**Action**: Either fix and retest, or proceed with caution if expected.

---

## Common Issues & Fixes

### "Backend Swagger UI not accessible"

**Symptom:**
```
[X] Backend Swagger UI not accessible
```

**Causes:**
- Backend not started
- Port 8000 in use
- API not listening on `0.0.0.0`

**Fix:**
```bash
# Check if backend running and healthy
docker compose -f docker-compose.prod.yml ps backend

# Check logs
docker compose -f docker-compose.prod.yml logs backend | tail -50

# If port conflict, modify docker-compose.prod.yml
# ports:
#   - "9000:8000"  # Use 9000 instead of 8000

# Restart
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### "Frontend HTML check failed"

**Symptom:**
```
[!] Frontend HTML check failed
```

**Causes:**
- Nginx not serving static files
- Frontend build failed
- CSS/JS loading causing HTML parse failure

**Fix:**
```bash
# Check frontend logs
docker compose -f docker-compose.prod.yml logs frontend

# Check nginx config in container
docker exec communityos-frontend cat /etc/nginx/conf.d/default.conf

# Rebuild frontend
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

### "Backend health check timed out"

**Symptom:**
```
[!] Backend health check may have timed out
```

**Causes:**
- Slow startup (database migrations)
- Insufficient memory
- Dependencies not installed

**Fix:**
```bash
# Give backend more startup time
# Edit STARTUP_WAIT in script: STARTUP_WAIT=30 or higher

# Check if migrations running
docker compose -f docker-compose.prod.yml logs backend | grep -i "alembic\|migration"

# Ensure requirements installed
docker compose -f docker-compose.prod.yml build --no-cache backend
```

### "communityos-network not found"

**Symptom:**
```
[X] communityos-network not found
```

**Causes:**
- Network not created (services not started)
- Previous test cleanup removed network

**Fix:**
```bash
# Restart services
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# Verify network
docker network ls | grep communityos
```

---

## Pre-Deployment Checklist

Before deploying to EC2, ensure:

- [ ] Run `./docker-test-prod.sh` (or `.bat`) locally
- [ ] All tests **pass** (exit code 0)
- [ ] No **failed** tests (red ✗)
- [ ] Review and address any **warnings** (yellow ⚠)
- [ ] Backend `.env` configured with production values:
  - [ ] DATABASE_URL points to production DB (Supabase/RDS)
  - [ ] AWS_S3_BUCKET and credentials set
  - [ ] RESEND_API_KEY or SES config set
  - [ ] SECRET_KEY is strong and unique
  - [ ] ENVIRONMENT=production
- [ ] docker-compose.prod.yml copied to EC2
- [ ] EC2 security group allows port 80 (frontend)
- [ ] EC2 security group allows port 8000 if API public (optional)

---

## EC2 Deployment

Once tests pass locally:

```bash
# 1. SSH to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# 2. Clone repo (or copy docker-compose.prod.yml)
git clone <your-repo> /opt/communityos
cd /opt/communityos

# 3. Create production .env
nano backend/.env
# Fill with production database URL, API keys, etc.

# 4. Deploy with production compose
docker compose -f docker-compose.prod.yml up --build -d

# 5. Verify health
docker compose -f docker-compose.prod.yml ps
docker logs communityos-backend --tail 20
docker logs communityos-frontend --tail 20

# 6. Access application
# http://<EC2-IP>/                    # Frontend
# http://<EC2-IP>:8000/api/docs       # Swagger UI
```

---

## Cleanup

### Automated Cleanup
```bash
# macOS/Linux - cleanup after tests
./docker-test-prod.sh --cleanup
```

### Manual Cleanup
```bash
# Stop and remove containers
docker compose -f docker-compose.prod.yml down

# Also remove volumes (CAUTION: deletes data)
docker compose -f docker-compose.prod.yml down -v

# Remove test .env file
rm backend/.env.prod.test
```

---

## Troubleshooting the Test Script Itself

### Script won't execute (Linux/macOS)
```bash
# Make executable
chmod +x docker-test-prod.sh

# Run with bash explicitly
bash docker-test-prod.sh
```

### sed command fails (macOS)
The script auto-detects macOS and uses correct `sed -i ''` syntax. If still issues:
```bash
# Manual sed (macOS):
sed -i '' 's/- "80:80"/- "8080:80"/g' docker-compose.prod.yml
```

### Colors not showing in output
- WSL: Use `wsl --update` or switch to Windows Terminal
- macOS: Use Terminal or iTerm2
- Linux: Colors should work; if not, remove color codes manually

---

## Reference

### Test Phases

1. **Prerequisites** (~1s) — Check tools installed
2. **Build** (~60s) — Build images
3. **Startup** (~30s) — Start containers + wait
4. **Health** (~5s) — Check HEALTHCHECK status
5. **Endpoints** (~10s) — Test API/frontend endpoints
6. **Resources** (~3s) — Check memory/CPU limits
7. **Networking** (~5s) — Test inter-container comm
8. **Volumes** (~3s) — Test volume write access
9. **Cleanup** (~5s) — Stop containers and report

**Total time**: ~120s (2 minutes)

### Exit Codes

```
0   = All tests passed; safe to deploy
1   = One or more tests failed; do not deploy
```

---

## Support

For issues or questions:

1. Check logs:
   ```bash
   docker compose -f docker-compose.prod.yml logs -f
   ```

2. Run with verbose output:
   ```bash
   bash -x docker-test-prod.sh  # Linux/macOS
   ```

3. Review DOCKER.md for architecture details

---

**Last Updated**: 2026-08-11  
**Tested On**: Docker 25.0+, Docker Compose 2.20+, Linux/macOS/Windows
