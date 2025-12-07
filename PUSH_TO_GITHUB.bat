@echo off
REM STM32-Practice Repository Push Helper
REM Run this script from PowerShell in your repository root

echo.
echo ========================================
echo STM32-Practice Git Push Helper
echo ========================================
echo.

cd /d E:\Backup\Tech_up

echo [1/7] Install Git LFS...
git lfs install

echo.
echo [2/7] Fetch latest remote state...
git fetch origin

echo.
echo [3/7] Show current local branches...
git branch -vv

echo.
echo [4/7] Show remote branches...
git ls-remote --heads origin

echo.
echo [5/7] Push develop branch...
git push origin develop

echo.
echo [6/7] Push main branch...
git push origin main

echo.
echo [7/7] Verify remote now has your commits...
git ls-remote --heads origin

echo.
echo ========================================
echo Done! Check https://github.com/maheshdarimireddi/stm32-practice
echo ========================================
echo.

pause
