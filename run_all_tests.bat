@echo off
setlocal EnableDelayedExpansion

set "RUN_PYSIDE2=0"
set "RUN_PYSIDE6=0"
set "CLEAN=0"

REM Parse command line arguments
if "%1"=="" (
    set "RUN_PYSIDE2=1"
    set "RUN_PYSIDE6=1"
) else (
    :parse_args
    if "%1"=="--help" (
        echo Usage: %0 [options]
        echo Options:
        echo   --pyside2  Run PySide2 tests only
        echo   --pyside6  Run PySide6 tests only
        echo   --clean    Force rebuild of virtual environments
        echo   --help     Show this help message
        exit /b 0
    )
    if "%1"=="--pyside2" set "RUN_PYSIDE2=1"
    if "%1"=="--pyside6" set "RUN_PYSIDE6=1"
    if "%1"=="--clean" set "CLEAN=1"
    shift
    if not "%1"=="" goto parse_args
)

if %RUN_PYSIDE2%==0 if %RUN_PYSIDE6%==0 (
    echo No test suite specified. Use --pyside2 and/or --pyside6
    exit /b 1
)

REM Store current directory and create package cache
set "INITIAL_DIR=%CD%"
if not exist ".package_cache" mkdir .package_cache

REM Download Python 3.7 if not already present and needed
if %RUN_PYSIDE2%==1 (
    set "PYTHON37_INSTALLER=.package_cache\python-3.7.9-amd64.exe"
    if not exist "python37" (
        if not exist "%PYTHON37_INSTALLER%" (
            echo Downloading Python 3.7...
            curl -o "%PYTHON37_INSTALLER%" https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe
        )
        echo Installing Python 3.7...
        "%PYTHON37_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 InstallLauncherAllUsers=0 TargetDir=%CD%\python37
    )
)

set "PYSIDE2_RESULT=0"
set "PYSIDE6_RESULT=0"

REM Run PySide2 tests if requested
if %RUN_PYSIDE2%==1 (
    echo.
    echo ===== Setting up PySide2 environment with Python 3.7 =====
    if %CLEAN%==1 call :clean_venv venv-pyside2
    if not exist "venv-pyside2" (
        %CD%\python37\python.exe -m venv venv-pyside2
        if errorlevel 1 (
            echo Failed to create PySide2 virtual environment
            exit /b 1
        )

        call venv-pyside2\Scripts\activate
        echo Installing dependencies for PySide2...
        python -m pip install --upgrade pip
        pip install --no-index --find-links=.package_cache pytest pytest-qt PySide2==5.15.2 || (
            pip download --dest=.package_cache pytest pytest-qt PySide2==5.15.2
            pip install --no-index --find-links=.package_cache pytest pytest-qt PySide2==5.15.2
        )
        pip install -e .
        if errorlevel 1 (
            echo Failed to install PySide2 dependencies
            call deactivate
            exit /b 1
        )
        call deactivate
    )

    echo Running tests with PySide2...
    call venv-pyside2\Scripts\activate.bat
    pytest tests -vv
    set PYSIDE2_RESULT=!errorlevel!
    call venv-pyside2\Scripts\deactivate.bat
    cd "%INITIAL_DIR%"
)

REM Run PySide6 tests if requested
if %RUN_PYSIDE6%==1 (
    echo.
    echo ===== Setting up PySide6 environment =====
    if %CLEAN%==1 call :clean_venv venv-pyside6
    if not exist "venv-pyside6" (
        python -m venv venv-pyside6
        if errorlevel 1 (
            echo Failed to create PySide6 virtual environment
            exit /b 1
        )

        call venv-pyside6\Scripts\activate
        echo Installing dependencies for PySide6...
        python -m pip install --upgrade pip
        pip install --no-index --find-links=.package_cache pytest pytest-qt PySide6 || (
            pip download --dest=.package_cache pytest pytest-qt PySide6
            pip install --no-index --find-links=.package_cache pytest pytest-qt PySide6
        )
        pip install -e .
        if errorlevel 1 (
            echo Failed to install PySide6 dependencies
            call deactivate
            exit /b 1
        )
        call deactivate
    )

    echo Running tests with PySide6...
    call venv-pyside6\Scripts\activate.bat
    pytest tests -vv
    set PYSIDE6_RESULT=!errorlevel!
    call venv-pyside6\Scripts\deactivate.bat
    cd "%INITIAL_DIR%"
)

echo.
echo ===== Test Results =====
if %RUN_PYSIDE2%==1 (
    if !PYSIDE2_RESULT! EQU 0 (
        echo PySide2 tests: PASSED
    ) else (
        echo PySide2 tests: FAILED
    )
)

if %RUN_PYSIDE6%==1 (
    if !PYSIDE6_RESULT! EQU 0 (
        echo PySide6 tests: PASSED
    ) else (
        echo PySide6 tests: FAILED
    )
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
