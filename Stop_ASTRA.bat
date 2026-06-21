@echo off
title Stop ASTRA Traffic Intelligence
echo ====================================================
echo Stopping ASTRA Traffic Intelligence Platform...
echo ====================================================
echo.
docker-compose down

echo.
echo ====================================================
echo All ASTRA services have been stopped safely!
echo ====================================================
echo.
pause
