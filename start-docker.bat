@echo off
REM =============================================
REM TalentFlow AI - Docker Startup Script (Windows)
REM Supports both GPU and CPU modes
REM =============================================

echo.
echo ========================================
echo  TalentFlow AI - Docker Deployment
echo ========================================
echo.

REM Check if Docker is running
echo [1/6] Checking Docker status...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and ensure it's running
    pause
    exit /b 1
)
echo Γ£à Docker is available

REM Check if .env file exists
echo.
echo [2/6] Checking environment configuration...
if not exist .env (
    echo WARNING: .env file not found
    echo Creating .env from template...
    copy .env.example .env >nul 2>&1
    echo.
    echo ΓÜáΓä╣´©ê  IMPORTANT: Please edit .env file with your Azure OpenAI credentials
    echo    You need to set:
    echo    - AZURE_OPENAI_API_KEY
    echo    - AZURE_OPENAI_ENDPOINT
    echo    - AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
    echo.
    set /p "continue=Press Enter to continue (make sure .env is configured)..."
) else (
    echo Γ£à .env file found
)

REM Check for GPU support
echo.
echo [3/6] Checking GPU availability...
docker run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi >nul 2>&1
if errorlevel 1 (
    set gpu_available=false
    echo WARNING: NVIDIA Container Toolkit not available
    echo GPU mode will not work. CPU mode recommended.
) else (
    set gpu_available=true
    echo Γ£à GPU support detected
)

REM Prompt for compute type
echo.
echo [4/6] Select compute mode:
echo.
if "%gpu_available%"=="true" (
    echo [G] GPU Mode - Fast, requires NVIDIA GPU (~10.5 GB container)
    echo     - Whisper medium model
    echo     - ~10x realtime transcription speed
    echo     - Requires NVIDIA Container Toolkit
    echo.
)
echo [C] CPU Mode - Slower, no GPU required (~2.5 GB container)
echo     - Whisper base model
echo     - ~0.5x realtime transcription speed
echo     - Works on any system
echo.

if "%gpu_available%"=="true" (
    set /p "mode=Enter choice (G/C): "
) else (
    echo GPU not available, defaulting to CPU mode...
    set mode=C
    timeout /t 3 >nul
)

REM Set profile and compose file based on selection
if /i "%mode%"=="G" (
    set profile=gpu
    set mode_name=GPU
    set container_size=~10.5 GB
) else (
    set profile=cpu
    set mode_name=CPU
    set container_size=~2.5 GB
)

REM Prompt for deployment type
echo.
echo [5/6] Select deployment mode:
echo [P] Production - Optimized builds, no hot-reload
echo [D] Development - Hot-reload, debugging enabled
echo.
set /p "deploy=Enter choice (P/D): "

if /i "%deploy%"=="D" (
    set compose_file=docker-compose.dev.yml
    set deploy_name=Development
) else (
    set compose_file=docker-compose.yml
    set deploy_name=Production
)

echo.
echo [6/6] Starting TalentFlow AI...
echo.
echo ========================================
echo  Configuration Summary
echo ========================================
echo  Compute Mode:    %mode_name%
echo  Deployment:      %deploy_name%
echo  Container Size:  %container_size%
echo  Profile:         %profile%
echo  Compose File:    %compose_file%
echo ========================================
echo.

REM Stop any existing containers
echo Stopping existing containers...
docker compose -f %compose_file% --profile gpu down >nul 2>&1
docker compose -f %compose_file% --profile cpu down >nul 2>&1

REM Start services with selected profile
echo Starting services with %mode_name% mode...
echo This may take several minutes on first run (downloading images)...
echo.

docker compose -f %compose_file% --profile %profile% up -d --build

if errorlevel 1 (
    echo.
    echo ΓáîΓä╣ Failed to start services
    echo.
    echo Common issues:
    if "%profile%"=="gpu" (
        echo - GPU mode requires NVIDIA Container Toolkit
        echo - Try CPU mode instead: Set mode=C and rerun
    ) else (
        echo - Check that .env file is properly configured
        echo - Ensure Docker has enough disk space (~3 GB)
    )
    echo.
    echo Check the error messages above for details
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Γ£ö TalentFlow AI Started Successfully!
echo ========================================
echo.
echo  Mode: %mode_name% (%container_size% backend)
echo  Deployment: %deploy_name%
echo.
echo Services available at:
echo  πÇ▒ Frontend (Streamlit): http://localhost:8501
echo  πï º Backend API:          http://localhost:8000
echo  πï ö API Documentation:    http://localhost:8000/docs
echo  Γ£ƒ´©ë´  MongoDB:              localhost:27017
echo.
echo Useful commands:
echo  View logs:    docker compose -f %compose_file% logs -f
echo  Stop all:     docker compose -f %compose_file% --profile %profile% down
echo  Restart:      docker compose -f %compose_file% --profile %profile% restart
echo.
echo Press Ctrl+C to view logs, or any key to exit...
set /p "logs=Show logs now? (Y/N): "
if /i "%logs%"=="Y" (
    docker compose -f %compose_file% logs -f
) else (
    echo.
    echo Services are running in the background
    echo Use 'docker compose -f %compose_file% logs -f' to view logs
)

pause