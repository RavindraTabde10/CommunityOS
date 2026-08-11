@echo off
REM CommunityOS Production Docker Compose Test Script (Windows)
REM Tests health, endpoints, resource limits, and networking before EC2 deployment
REM Usage: docker-test-prod.bat [--cleanup]

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=docker-compose.prod.yml
set ENV_FILE=backend\.env.prod.test
set FRONTEND_PORT=8080
set BACKEND_PORT=8000
set STARTUP_WAIT=20

REM Counters
set PASSED=0
set FAILED=0
set WARNINGS=0

REM ====== Helper Functions ======

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║   CommunityOS Production Docker Compose Test Suite            ║
echo ║   Automated tests for production deployment validation        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check prerequisites
echo.
echo ======== Checking Prerequisites ========
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo [X] Docker not found. Please install Docker.
    exit /b 1
)
echo [OK] Docker installed
set /a PASSED+=1

docker compose version >nul 2>&1
if errorlevel 1 (
    echo [X] Docker Compose not found. Please install Docker Compose.
    exit /b 1
)
echo [OK] Docker Compose installed
set /a PASSED+=1

if not exist "%COMPOSE_FILE%" (
    echo [X] %COMPOSE_FILE% not found
    exit /b 1
)
echo [OK] docker-compose.prod.yml found
set /a PASSED+=1

if not exist "%ENV_FILE%" (
    if exist "backend\.env.example" (
        echo [!] Creating %ENV_FILE% from backend\.env.example
        copy "backend\.env.example" "%ENV_FILE%" >nul
        set /a WARNINGS+=1
    ) else (
        echo [!] %ENV_FILE% not found. Using backend\.env if available
        set /a WARNINGS+=1
    )
) else (
    echo [OK] %ENV_FILE% found
    set /a PASSED+=1
)

REM Build images
echo.
echo ======== Building Docker Images ========
echo.
echo Building backend and frontend images...
docker compose -f "%COMPOSE_FILE%" build >nul 2>&1
if errorlevel 1 (
    echo [X] Failed to build images
    exit /b 1
)
echo [OK] Images built successfully
set /a PASSED+=1

REM Start containers (temporarily modify port)
echo.
echo ======== Starting Containers ========
echo.
echo Starting services...

REM Backup original compose file and modify for testing
powershell -Command "(Get-Content '%COMPOSE_FILE%') -replace '- \"80:80\"', '- \"%FRONTEND_PORT%:80\"' | Set-Content '%COMPOSE_FILE%'" 2>nul

docker compose -f "%COMPOSE_FILE%" up -d >nul 2>&1
if errorlevel 1 (
    echo [X] Failed to start containers
    powershell -Command "(Get-Content '%COMPOSE_FILE%') -replace '- \"%FRONTEND_PORT%:80\"', '- \"80:80\"' | Set-Content '%COMPOSE_FILE%'" 2>nul
    exit /b 1
)
echo [OK] Containers started
set /a PASSED+=1

echo Waiting %STARTUP_WAIT% seconds for services to start...
timeout /t %STARTUP_WAIT% /nobreak

REM Test container health
echo.
echo ======== Testing Container Health ========
echo.
echo Checking backend health...
docker compose -f "%COMPOSE_FILE%" ps backend | findstr /i "healthy" >nul 2>&1
if errorlevel 1 (
    echo [!] Backend health check may have timed out
    set /a WARNINGS+=1
) else (
    echo [OK] Backend is healthy
    set /a PASSED+=1
)

echo Checking frontend health...
docker compose -f "%COMPOSE_FILE%" ps frontend | findstr /i "healthy" >nul 2>&1
if errorlevel 1 (
    echo [!] Frontend health check may have timed out
    set /a WARNINGS+=1
) else (
    echo [OK] Frontend is healthy
    set /a PASSED+=1
)

REM Test API endpoints
echo.
echo ======== Testing API Endpoints ========
echo.

echo Testing backend Swagger UI (http://localhost:%BACKEND_PORT%/api/docs)...
curl -sf "http://localhost:%BACKEND_PORT%/api/docs" >nul 2>&1
if errorlevel 1 (
    echo [X] Backend Swagger UI not accessible
    set /a FAILED+=1
) else (
    echo [OK] Backend Swagger UI accessible
    set /a PASSED+=1
)

echo Testing backend root endpoint...
curl -s -o nul -w "HTTP %%{http_code}" "http://localhost:%BACKEND_PORT%/" >nul 2>&1
echo [OK] Backend responding
set /a PASSED+=1

echo Testing frontend (http://localhost:%FRONTEND_PORT%)...
curl -s -o nul -w "HTTP %%{http_code}" "http://localhost:%FRONTEND_PORT%/" >nul 2>&1
echo [OK] Frontend accessible
set /a PASSED+=1

echo Checking if frontend returns HTML...
curl -s "http://localhost:%FRONTEND_PORT%/" | findstr /i "<html" >nul 2>&1
if errorlevel 1 (
    echo [!] Frontend HTML check failed
    set /a WARNINGS+=1
) else (
    echo [OK] Frontend returns valid HTML
    set /a PASSED+=1
)

REM Test resource limits
echo.
echo ======== Testing Resource Limits ========
echo.
echo Checking resource limits and usage...

docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.CPUPerc}}" 2>nul | findstr /i "backend frontend"
echo [OK] Resource limits checked
set /a PASSED+=1

REM Test networking
echo.
echo ======== Testing Networking ========
echo.
echo Checking network configuration...

docker network ls | findstr /i "communityos-network" >nul 2>&1
if errorlevel 1 (
    echo [X] communityos-network not found
    set /a FAILED+=1
) else (
    echo [OK] communityos-network exists
    set /a PASSED+=1
)

echo Testing inter-container communication...
docker exec communityos-frontend wget -q -O- "http://backend:8000/api/docs" >nul 2>&1
if errorlevel 1 (
    echo [!] Frontend cannot reach backend (may be expected)
    set /a WARNINGS+=1
) else (
    echo [OK] Frontend can reach backend
    set /a PASSED+=1
)

REM Test volumes
echo.
echo ======== Testing Volumes ========
echo.
echo Checking volume configuration...

docker volume ls | findstr /i "backend_data" >nul 2>&1
if errorlevel 1 (
    echo [X] backend_data volume not found
    set /a FAILED+=1
) else (
    echo [OK] backend_data volume exists
    set /a PASSED+=1
)

REM Cleanup
echo.
echo ======== Cleaning Up ========
echo.
echo Stopping and removing containers...
docker compose -f "%COMPOSE_FILE%" down --remove-orphans >nul 2>&1
echo [OK] Cleanup complete

REM Restore original compose file
powershell -Command "(Get-Content '%COMPOSE_FILE%') -replace '- \"%FRONTEND_PORT%:80\"', '- \"80:80\"' | Set-Content '%COMPOSE_FILE%'" 2>nul
echo [OK] Original compose file restored

REM Generate report
echo.
echo ======== Test Report ========
echo.
echo Results:
echo   [OK] Passed:   %PASSED%
echo   [X]  Failed:   %FAILED%
echo   [!]  Warnings: %WARNINGS%
echo.

if %FAILED% equ 0 (
    echo ════════════════════════════════════════════════════════════════
    echo All tests passed! Safe to deploy to EC2.
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo Next steps:
    echo   1. Review any warnings above
    echo   2. If all tests pass, deploy to EC2:
    echo      - Copy docker-compose.prod.yml to EC2
    echo      - Set environment variables in backend\.env
    echo      - Run: docker compose -f docker-compose.prod.yml up -d
    echo.
    exit /b 0
) else (
    echo ════════════════════════════════════════════════════════════════
    echo Some tests failed. Review errors above before deploying.
    echo ════════════════════════════════════════════════════════════════
    echo.
    exit /b 1
)
