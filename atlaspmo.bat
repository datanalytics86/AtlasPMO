@echo off
cd /d "%~dp0"
set "PATH=%APPDATA%\Python\Python312\Scripts;%USERPROFILE%\.local\bin;%PATH%"
uv run python -m streamlit run src/atlaspmo/ui/app.py
