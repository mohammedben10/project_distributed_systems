@echo off
title Plant Disease Detection — Launcher
color 0A

echo.
echo  ============================================================
echo    Plant Disease Detection System — Starting Services...
echo  ============================================================
echo.

:: ---------------------------------------------------------------
:: CONFIGURATION
:: ---------------------------------------------------------------
set ROOT=%~dp0
set AI_DIR=%ROOT%ai_service
set WEB_DIR=%ROOT%web_gateway

:: ---------------------------------------------------------------
:: DETECT PYTHON EXECUTABLE
:: Try: python -> py -> common install paths
:: ---------------------------------------------------------------
set PYTHON=

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py
    goto :python_found
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set PYTHON="%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    goto :python_found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :python_found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :python_found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :python_found
)

color 0C
echo  [ERROR] Python could not be found on this machine.
echo.
echo  Please install Python from https://www.python.org/downloads/
echo  and check "Add python.exe to PATH" during install.
echo.
pause
exit /b 1

:python_found
echo  [OK] Python found ^(%PYTHON%^)
echo.

:: ---------------------------------------------------------------
:: INSTALL DEPENDENCIES (only if needed)
:: ---------------------------------------------------------------
echo  Checking / installing dependencies...
echo.

echo  [AI SERVICE] Installing requirements...
%PYTHON% -m pip install -r "%AI_DIR%\requirements.txt" --quiet --disable-pip-version-check
if errorlevel 1 (
    color 0C
    echo  [ERROR] Failed to install AI service dependencies.
    echo  Check %AI_DIR%\requirements.txt and your internet connection.
    pause
    exit /b 1
)
echo  [AI SERVICE] Dependencies OK.

echo  [DJANGO   ] Installing requirements...
%PYTHON% -m pip install -r "%WEB_DIR%\requirements.txt" --quiet --disable-pip-version-check
if errorlevel 1 (
    color 0C
    echo  [ERROR] Failed to install web gateway dependencies.
    echo  Check %WEB_DIR%\requirements.txt and your internet connection.
    pause
    exit /b 1
)
echo  [DJANGO   ] Dependencies OK.
echo.

:: ---------------------------------------------------------------
:: LAUNCH AI SERVICE (gRPC Server — port 50051)
:: ---------------------------------------------------------------
echo  [1/2] Starting AI gRPC Server on port 50051...

if exist "%AI_DIR%\venv\Scripts\activate.bat" (
    start "AI gRPC Server [port 50051]" cmd /k "color 0B && cd /d "%AI_DIR%" && call venv\Scripts\activate.bat && echo [AI SERVICE] venv activated && echo [AI SERVICE] Starting gRPC server... && %PYTHON% server.py"
) else if exist "%AI_DIR%\.venv\Scripts\activate.bat" (
    start "AI gRPC Server [port 50051]" cmd /k "color 0B && cd /d "%AI_DIR%" && call .venv\Scripts\activate.bat && echo [AI SERVICE] venv activated && echo [AI SERVICE] Starting gRPC server... && %PYTHON% server.py"
) else (
    start "AI gRPC Server [port 50051]" cmd /k "color 0B && cd /d "%AI_DIR%" && echo [AI SERVICE] Starting gRPC server... && %PYTHON% server.py"
)

:: Wait for gRPC server to initialize before starting Django
echo  [  ] Waiting 5 seconds for gRPC server to initialize...
timeout /t 5 /nobreak >nul

:: ---------------------------------------------------------------
:: LAUNCH WEB GATEWAY (Django — port 8000)
:: ---------------------------------------------------------------
echo  [2/2] Starting Django Web Gateway on http://127.0.0.1:8000 ...

if exist "%WEB_DIR%\venv\Scripts\activate.bat" (
    start "Django Web Gateway [port 8000]" cmd /k "color 0E && cd /d "%WEB_DIR%" && call venv\Scripts\activate.bat && echo [DJANGO] venv activated && echo [DJANGO] Applying migrations... && %PYTHON% manage.py migrate --run-syncdb && echo [DJANGO] Starting server... && %PYTHON% manage.py runserver"
) else if exist "%WEB_DIR%\.venv\Scripts\activate.bat" (
    start "Django Web Gateway [port 8000]" cmd /k "color 0E && cd /d "%WEB_DIR%" && call .venv\Scripts\activate.bat && echo [DJANGO] venv activated && echo [DJANGO] Applying migrations... && %PYTHON% manage.py migrate --run-syncdb && echo [DJANGO] Starting server... && %PYTHON% manage.py runserver"
) else (
    start "Django Web Gateway [port 8000]" cmd /k "color 0E && cd /d "%WEB_DIR%" && echo [DJANGO] Applying migrations... && %PYTHON% manage.py migrate --run-syncdb && echo [DJANGO] Starting server... && %PYTHON% manage.py runserver"
)

:: ---------------------------------------------------------------
:: DONE
:: ---------------------------------------------------------------
echo.
echo  ============================================================
echo    Both services launched in separate windows!
echo.
echo    AI gRPC Server  -->  localhost:50051
echo    Django Web App  -->  http://127.0.0.1:8000
echo  ============================================================
echo.
echo  Press any key to open the app in your browser...
pause >nul
start http://127.0.0.1:8000

exit /b 0
