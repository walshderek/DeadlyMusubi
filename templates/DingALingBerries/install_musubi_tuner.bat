@echo off
setlocal ENABLEDELAYEDEXPANSION

echo =====================================================
echo   FaceTrainer - Musubi Tuner Installer
echo   - Installs musubi-tuner at commit e7adb86
echo   - Pins Torch 2.8.0+cu128 and TorchVision 0.23.0+cu128
echo   - Uses local 2.8.0+cu128 wheel if present
echo =====================================================
echo.

REM --- Determine script directory and work there ---
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM --- Check for git ---
where git >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Git was not found in PATH.
    echo         Please install Git for Windows and try again.
    echo.
    pause
    exit /b 1
)

REM --- Check for Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found in PATH.
    echo         Please install Python 3.10+ (add to PATH) and try again.
    echo.
    pause
    exit /b 1
)

REM Use the first python found
for /f "delims=" %%P in ('where python') do (
    set "SYS_PYTHON=%%P"
    goto :got_python
)

:got_python
echo [INFO] Using Python: "%SYS_PYTHON%"
echo.

REM --- Detect Python major.minor (3.10, 3.11, 3.12, 3.13) ---
for /f "usebackq delims=" %%V in (`"%SYS_PYTHON%" -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"`) do (
    set "PY_VER=%%V"
)

echo [INFO] Detected Python version: %PY_VER%
echo.

REM --- Clone musubi-tuner into THIS folder (no extra nesting) ---
if not exist "musubi-tuner" (
    echo [INFO] Cloning musubi-tuner into:
    echo        "%SCRIPT_DIR%musubi-tuner"
    git clone https://github.com/kohya-ss/musubi-tuner.git musubi-tuner
    if errorlevel 1 (
        echo [ERROR] git clone failed.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [INFO] "musubi-tuner" folder already exists. Skipping clone.
)
echo.

cd /d "%SCRIPT_DIR%musubi-tuner"

REM --- Checkout the exact commit/tag you want (v0.2.8: e7adb86) ---
echo [INFO] Checking out musubi-tuner commit e7adb86 (v0.2.8)...
git fetch --all >nul 2>&1
git checkout e7adb86
if errorlevel 1 (
    echo [ERROR] git checkout e7adb86 failed.
    echo.
    pause
    exit /b 1
)
echo.

REM --- Create / reuse venv inside musubi-tuner ---
if not exist "venv" (
    echo [INFO] Creating virtual environment "venv"...
    "%SYS_PYTHON%" -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Reusing existing virtual environment "venv".
)
echo.

set "VENV_PY=%CD%\venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo [ERROR] venv Python not found at:
    echo         "%VENV_PY%"
    echo.
    pause
    exit /b 1
)

echo [INFO] Upgrading pip in venv...
"%VENV_PY%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip/setuptools/wheel in venv.
    echo.
    pause
    exit /b 1
)
echo.

REM ====================================================
REM  Install Torch 2.8.0+cu128 and TorchVision 0.23.0+cu128
REM ====================================================

REM Map Python version to proper cp tag for local wheel
set "PY_TAG="
if "%PY_VER%"=="3.10" set "PY_TAG=cp310-cp310"
if "%PY_VER%"=="3.11" set "PY_TAG=cp311-cp311"
if "%PY_VER%"=="3.12" set "PY_TAG=cp312-cp312"
if "%PY_VER%"=="3.13" set "PY_TAG=cp313-cp313"

set "LOCAL_WHEEL="
if defined PY_TAG (
    set "LOCAL_WHEEL=tor ch-2.8.0+cu128-%PY_TAG%-win_amd64.whl"
)

REM Fix accidental space in variable name above (batch quirk protection)
set "LOCAL_WHEEL=%LOCAL_WHEEL:tor ch=torch%"

set "LOCAL_WHEEL_PATH=%SCRIPT_DIR%%LOCAL_WHEEL%"

echo [INFO] Installing PyTorch 2.8.0+cu128 and TorchVision 0.23.0+cu128...
if exist "%LOCAL_WHEEL_PATH%" (
    echo [INFO] Found local torch wheel:
    echo        "%LOCAL_WHEEL_PATH%"
    echo [INFO] Installing local torch wheel into venv...
    "%VENV_PY%" -m pip install "%LOCAL_WHEEL_PATH%"
    if errorlevel 1 (
        echo [ERROR] Failed to install local torch wheel.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [INFO] No local torch wheel found for this Python (%PY_VER%).
    echo [INFO] Downloading torch==2.8.0+cu128 from PyTorch cu128 index...
    "%VENV_PY%" -m pip install "torch==2.8.0+cu128" --index-url https://download.pytorch.org/whl/cu128
    if errorlevel 1 (
        echo [ERROR] Failed to install torch==2.8.0+cu128 from PyTorch index.
        echo.
        pause
        exit /b 1
    )
)

echo [INFO] Installing torchvision==0.23.0+cu128 from PyTorch cu128 index...
"%VENV_PY%" -m pip install "torchvision==0.23.0+cu128" --index-url https://download.pytorch.org/whl/cu128
if errorlevel 1 (
    echo [ERROR] Failed to install torchvision==0.23.0+cu128.
    echo.
    pause
    exit /b 1
)
echo.

REM --- Create constraint file so Musubi cannot override Torch/TorchVision ---
echo [INFO] Creating torch_constraints.txt with pinned versions...
>torch_constraints.txt echo torch==2.8.0+cu128
>>torch_constraints.txt echo torchvision==0.23.0+cu128
echo [INFO] Created "%CD%\torch_constraints.txt"
echo.

REM --- Install musubi-tuner in editable mode with constraints applied ---
echo [INFO] Installing musubi-tuner (editable, constrained to Torch 2.8.0+cu128)...
"%VENV_PY%" -m pip install -e . -c torch_constraints.txt
if errorlevel 1 (
    echo [ERROR] pip install -e . (musubi-tuner) failed.
    echo.
    pause
    exit /b 1
)
echo.

echo =====================================================
echo   Musubi Tuner install complete.
echo   Location : %SCRIPT_DIR%musubi-tuner
echo   Python   : %VENV_PY%
echo   Torch    : 2.8.0+cu128 (pinned via torch_constraints.txt)
echo   TVision  : 0.23.0+cu128
echo =====================================================
echo.
echo You can now use this Musubi install from your FaceTrainer GUI.
echo.
pause
endlocal
exit /b 0
