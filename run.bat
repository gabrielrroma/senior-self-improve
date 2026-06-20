@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 "%SCRIPT_DIR%app.py"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        python "%SCRIPT_DIR%app.py"
    ) else (
        echo Python nao encontrado.
        echo Instale o Python 3.10+ e tente novamente.
        echo Se preferir, rode: py -3 "%SCRIPT_DIR%app.py"
        pause
    )
)
