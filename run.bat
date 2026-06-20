@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "LOCAL_PYTHON=%LocalAppData%\Programs\Python\Python312\python.exe"
set "PYTHON_HOME=%LocalAppData%\Programs\Python\Python312"

if not defined TCL_LIBRARY set "TCL_LIBRARY=%PYTHON_HOME%\tcl\tcl8.6"
if not defined TK_LIBRARY set "TK_LIBRARY=%PYTHON_HOME%\tcl\tk8.6"

python --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python "%SCRIPT_DIR%app.py"
    goto :end
)

if exist "%LOCAL_PYTHON%" (
    "%LOCAL_PYTHON%" "%SCRIPT_DIR%app.py"
    goto :end
)

py -3 --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 "%SCRIPT_DIR%app.py"
) else (
    echo Python nao encontrado.
    echo Instale o Python 3.10+ e tente novamente.
    pause
)

:end
endlocal
