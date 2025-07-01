@echo off
setlocal enabledelayedexpansion

REM Fast Docker build script for Windows
REM Usage: build-fast.bat [--multi-stage] [--no-cache]

REM Enable BuildKit for faster builds
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1

REM Parse arguments
set MULTI_STAGE=false
set NO_CACHE=

:parse_args
if "%1"=="" goto :build
if "%1"=="--multi-stage" (
    set MULTI_STAGE=true
    shift
    goto :parse_args
)
if "%1"=="--no-cache" (
    set NO_CACHE=--no-cache
    shift
    goto :parse_args
)
echo Unknown option: %1
echo Usage: %0 [--multi-stage] [--no-cache]
exit /b 1

:build
echo 🚀 Starting fast Docker build...
echo BuildKit enabled: %DOCKER_BUILDKIT%
echo Multi-stage build: %MULTI_STAGE%
echo No cache: %NO_CACHE%

REM Choose Dockerfile based on arguments
if "%MULTI_STAGE%"=="true" (
    echo 📦 Using multi-stage Dockerfile.backend.optimized
    copy Dockerfile.backend.optimized Dockerfile.backend.temp
) else (
    echo 📦 Using optimized single-stage Dockerfile.backend
)

REM Build with BuildKit
echo 🔨 Building containers...
docker-compose build %NO_CACHE% --parallel

REM Clean up temp file if used
if "%MULTI_STAGE%"=="true" (
    del Dockerfile.backend.temp
)

echo ✅ Build completed successfully!
echo 🚀 Starting containers...
docker-compose up -d

echo 🎉 All done! Your Bug Bounty Platform is running.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 🌺 Flower (Celery): http://localhost:5555

pause 