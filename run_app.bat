@echo off
REM Script de lancement de l'application Streamlit
REM Prompt-Firewall Multi-Model Platform

echo ============================================
echo   Prompt Firewall - Multi-Model Platform
echo ============================================
echo.

REM Vérifier si streamlit est installé
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [ERREUR] Streamlit n'est pas installe!
    echo.
    echo Installez les dependances avec:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [OK] Streamlit detecte
echo.
echo Lancement de l'application...
echo.
echo URL: http://localhost:8501
echo.

REM Lancer l'application
python -m streamlit run apps/streamlit_app.py

pause
