@echo off
echo ========================================
echo Starting TalentFlow AI Backend
echo ========================================
echo.
echo Activating conda environment 'uday'...
call conda activate uday
echo.
echo Starting backend server...
cd Backend
python main.py
pause

