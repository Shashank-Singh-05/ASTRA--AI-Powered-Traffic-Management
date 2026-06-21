@echo off
title ASTRA Traffic Intelligence Platform
echo ====================================================
echo Starting ASTRA Traffic Intelligence Platform...
echo ====================================================
echo.
echo Make sure Docker Desktop is running!
echo.
echo Launching the database, backend AI models, and frontend...
docker-compose up --build -d

echo.
echo ====================================================
echo ASTRA is starting in the background!
echo ====================================================
echo.
echo Waiting for servers to initialize (this takes about 10 seconds)...
timeout /t 10 /nobreak > NUL

echo.
echo Opening the ASTRA Dashboard in your default web browser...
start http://localhost:5173

echo.
echo You can close this window now. The servers will continue running in Docker.
echo To stop the servers later, run the "Stop_ASTRA" shortcut.
echo.
pause
