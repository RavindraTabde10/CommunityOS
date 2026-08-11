# Feature Plan: AWS EC2 Docker Deployment

**Feature:** AWS EC2 Docker Deployment
**Date:** 2026-08-11
**Priority:** Medium
**Estimated Complexity:** Medium (1–3 days)
**Status:** 📋 Planning

---

## 1. Objective

> Deploy the CommunityOS application to AWS using EC2 instances and Docker containers, enabling a reproducible production-like environment with both backend and frontend services containerized and running together.

**User Stories:**
- As a developer, I can build and run the backend and frontend as Docker containers so that the application is deployable in a consistent environment.
- As an operations engineer, I can launch an AWS EC2 instance, deploy the Dockerized application, and keep it running reliably so that the service is available to users.

**Out of Scope (for this plan):**
- AWS-managed Kubernetes deployment (EKS)
- Production-grade autoscaling, load balancing, or multi-AZ networking
- CI/CD pipeline automation
- Database migration to managed AWS database services like RDS

---

## 2. Backward Compatibility Gate ⚠️

- [ ] Does a backend endpoint for this already exist? No — deployment is infrastructure-focused.
- [ ] Does a service for this already exist? No — this is environment and packaging work.
- [ ] Does a frontend page/route for this already exist? No.
- [ ] Does a model for this already exist? No.
- [ ] Does an Alembic migration for this schema change already exist? No.
- [ ] Will any existing endpoint path change? No.
- [ ] Will any existing Pydantic field be removed? No.
- [ ] Will any existing Redux action be removed? No.

---

## 3. Backend Changes

### 3a. New Database Model(s)

> Not applicable. Deployment does not require schema changes.

---

### 3b. Alembic Migration

> Not applicable. No database schema change.

---

### 3c. Pydantic Schemas

> Not applicable. No schema change.

---

### 3d. Service Layer

> Not applicable. Deployment does not change application business logic.

---

### 3e. API Endpoints

> Not applicable. Existing API remains unchanged.

---

## 4. Frontend Changes

### 4a. API Service

> Not applicable. Frontend service code remains unchanged.

---

### 4b. New Pages

> Not applicable.

---

### 4c. New Components (if needed)

> Not applicable.

---

### 4d. Route Registration

> Not applicable.

---

### 4e. Sidebar Navigation

> Not applicable.

---

### 4f. Dashboard Widget (optional)

- [ ] New widget needed? No

---

## 5. Agent Execution Order

Phase 1 — Deployment Packaging
  1. Add Dockerfiles for the backend and frontend.
  2. Add a root-level `docker-compose.yml` to orchestrate both services.
  3. Add `.dockerignore` files for backend and frontend.
  4. Validate container build locally.
  5. ✅ VERIFY: backend and frontend containers start without error locally.

Phase 2 — AWS EC2 Provisioning
  6. Document AWS EC2 launch steps and required IAM privileges.
  7. Document required security group settings for HTTP/HTTPS and SSH.
  8. Document EC2 instance setup commands for Docker, Docker Compose, and app deployment.
  9. ✅ VERIFY: a test EC2 instance can pull images and run the application.

Phase 3 — Run and Validate
  10. Start services with Docker Compose on EC2.
  11. Verify application accessibility via the EC2 public URL.
  12. Monitor logs and ensure the app stays running.
  13. ✅ VERIFY: both backend and frontend are reachable and functional.

Phase 4 — Documentation
  14. Update `README.md` and `QUICKSTART.md` with deployment instructions.
  15. Update `INDEX.md` if new deployment files are added.
  16. ✅ VERIFY: documentation is complete and correct.

---

## 6. Verification Checklist

**Deployment Packaging:**
- [ ] Backend Dockerfile builds successfully.
- [ ] Frontend Dockerfile builds successfully.
- [ ] `docker-compose.yml` starts both services together.
- [ ] Local containerized app runs and serves backend and frontend.

**AWS EC2 Provisioning:**
- [ ] EC2 instance launched and reachable.
- [ ] Docker and Docker Compose installed on EC2.
- [ ] Application containers start successfully on EC2.
- [ ] Service is reachable through the instance public IP or DNS.

**Run & Validation:**
- [ ] Backend API responds to requests from the deployed EC2 instance.
- [ ] Frontend loads and communicates with the backend.
- [ ] Logs are available and show no fatal startup errors.

**Documentation:**
- [ ] `README.md` includes deployment steps for AWS EC2.
- [ ] Deployment documentation notes environment variables and config requirements.
- [ ] No outdated or placeholder text remains.

---

## 7. Documentation Updates

> The agent updates all relevant documentation after deployment packaging and validation.

| File | What to update |
|------|---------------|
| `README.md` | Add AWS EC2 deployment instructions and Docker Compose usage |
| `QUICKSTART.md` | Add a summary of AWS EC2 deployment prerequisites and commands |
| `INDEX.md` | Add any new Docker or deployment files to the project structure if significant |
| `backend/API_README.md` | No update required unless deployment changes runtime config |

---

## 8. New Dependencies

**Backend (`requirements.txt`):**
- None

**Frontend (`package.json`):**
- None

**New environment variables (add to `backend/.env.template`):**
- None

---

## 9. Rollback Plan

If deployment changes cause issues:
1. Revert Dockerfile or Compose changes from source control.
2. Stop and remove the Docker containers on EC2.
3. Roll back EC2 instance to a previous AMI snapshot or terminate it and launch a replacement.
4. Revert documentation changes if they are incorrect.
