@echo off
setlocal EnableDelayedExpansion

echo ===== Running tests with both PySide2 and PySide6 =====

REM Store current directory and create package cache
set "INITIAL_DIR=%CD%"
if not exist ".package_cache" mkdir .package_cache

REM Download Python 3.7 if not already present
set "PYTHON37_INSTALLER=.package_cache\python-3.7.9-amd64.exe"
if not exist "python37" (
    if not exist "%PYTHON37_INSTALLER%" (
        echo Downloading Python 3.7...
        curl -o "%PYTHON37_INSTALLER%" https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe
    )
    echo Installing Python 3.7...
    "%PYTHON37_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 InstallLauncherAllUsers=0 TargetDir=%CD%\python37
)

REM PySide2 Tests with Python 3.7
echo.
echo ===== Setting up PySide2 environment with Python 3.7 =====
call :clean_venv venv-pyside2
%CD%\python37\python.exe -m venv venv-pyside2
if errorlevel 1 (
    echo Failed to create PySide2 virtual environment
    exit /b 1
)

call venv-pyside2\Scripts\activate
echo Installing dependencies for PySide2...
python -m pip install --upgrade pip
pip install --no-index --find-links=.package_cache pytest PySide2==5.15.2 || (
    pip download --dest=.package_cache pytest PySide2==5.15.2
    pip install --no-index --find-links=.package_cache pytest PySide2==5.15.2
)
pip install -e .
if errorlevel 1 (
    echo Failed to install PySide2 dependencies
    call deactivate
    exit /b 1
)

echo Running tests with PySide2...
pytest tests/unit/test_qtcompat.py -v
set PYSIDE2_RESULT=!errorlevel!
call deactivate
cd "%INITIAL_DIR%"

REM PySide6 Tests with current Python
echo.
echo ===== Setting up PySide6 environment =====
call :clean_venv venv-pyside6
python -m venv venv-pyside6
if errorlevel 1 (
    echo Failed to create PySide6 virtual environment
    exit /b 1
)

call venv-pyside6\Scripts\activate
echo Installing dependencies for PySide6...
python -m pip install --upgrade pip
pip install --no-index --find-links=.package_cache pytest PySide6 || (
    pip download --dest=.package_cache pytest PySide6
    pip install --no-index --find-links=.package_cache pytest PySide6
)
pip install -e .
if errorlevel 1 (
    echo Failed to install PySide6 dependencies
    call deactivate
    exit /b 1
)

echo Running tests with PySide6...
pytest tests/unit/test_qtcompat.py -v
set PYSIDE6_RESULT=!errorlevel!
call deactivate
cd "%INITIAL_DIR%"

echo.
echo ===== Test Results =====
if !PYSIDE2_RESULT! EQU 0 (
    echo PySide2 tests: PASSED
) else (
    echo PySide2 tests: FAILED
)

if !PYSIDE6_RESULT! EQU 0 (
    echo PySide6 tests: PASSED
) else (
    echo PySide6 tests: FAILED
)

if !PYSIDE2_RESULT! NEQ 0 exit /b !PYSIDE2_RESULT!
if !PYSIDE6_RESULT! NEQ 0 exit /b !PYSIDE6_RESULT!

echo.
echo All tests completed successfully!
exit /b 0

:clean_venv
if exist "%~1" (
    echo Removing existing virtual environment: %~1
    rmdir /s /q "%~1"
)
goto :eof
