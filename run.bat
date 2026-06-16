@echo off
title HMS Launcher

cd Hospital_managment
call venv\Scripts\activate

start cmd /k python manage.py runserver

timeout /t 4 >nul
start http://127.0.0.1:8000