@echo off
title HMS Installer

echo ==============================
echo     HMS FULL INSTALLER
echo ==============================

REM ----------------------------
REM CHECK PYTHON
REM ----------------------------
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ and tick "Add to PATH"
    pause
    exit /b
)

echo Python OK ✔

REM ----------------------------
REM CHECK PIP
REM ----------------------------
python -m pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Pip missing, bootstrapping pip...
    python -m ensurepip --upgrade
)

echo Pip OK ✔

REM ----------------------------
REM UPGRADE PIP
REM ----------------------------
echo Upgrading pip...
python -m pip install --upgrade pip

REM ----------------------------
REM GO TO PROJECT
REM ----------------------------
cd Hospital_managment

REM ----------------------------
REM VENV SETUP
REM ----------------------------
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

REM ----------------------------
REM INSTALL REQUIREMENTS
REM ----------------------------
echo Installing dependencies...
python -m pip install -r requirements.txt

REM ----------------------------
REM DJANGO SETUP
REM ----------------------------
echo Running migrations...
python manage.py migrate

echo ==============================
echo   SETUP COMPLETE ✔
echo ==============================
pause

echo ==============================
echo SETUP COMPLETE ✔
echo ==============================

echo Starting HMS server...

call run.bat

pause