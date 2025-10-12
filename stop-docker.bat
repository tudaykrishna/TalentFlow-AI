@echo off
REM =============================================
REM TalentFlow AI - Docker Stop Script (Windows)
REM =============================================

echo.
echo ========================================
echo  TalentFlow AI - Stopping Services
echo ========================================
echo.

REM Stop production services
echo Stopping production services...
docker compose -f docker-compose.yml down >nul 2>&1

REM Stop development services  
echo Stopping development services...
docker compose -f docker-compose.dev.yml down >nul 2>&1

echo.
echo ✅ All TalentFlow AI services stopped
echo.

REM Ask about cleanup
set /p "cleanup=Remove all data (volumes)? This will delete all data! (y/N): "
if /i "%cleanup%"=="y" (
    echo.
    echo Removing all volumes and data...
    docker compose -f docker-compose.yml down -v --remove-orphans >nul 2>&1
    docker compose -f docker-compose.dev.yml down -v --remove-orphans >nul 2>&1
    
    REM Clean up unused images
    echo Cleaning up unused Docker images...
    docker image prune -f >nul 2>&1
    
    echo ✅ All data and containers removed
) else (
    echo Data preserved. Use 'docker compose up -d' to restart.
)

echo.
pause
