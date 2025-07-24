@echo off
REM ============================================================
REM Japanese ASMR Audio Downloader - Final Distribution Version
REM ============================================================

REM Force UTF-8 encoding for Korean text
chcp 65001 > nul 2>&1

REM Set environment variables for proper encoding
set PYTHONIOENCODING=utf-8
set LANG=ko_KR.UTF-8

REM Set console size for better display
mode con: cols=85 lines=25

title Japanese ASMR Audio Downloader

cls
echo.
echo ================================================================
echo                Japanese ASMR Audio Downloader                
echo                  [ASMR 오디오 다운로더 v1.1]  
echo                       By noName_Come                   
echo ================================================================
echo.

REM Create mp3 directory first
if not exist "mp3" (
    mkdir mp3
    echo [디렉토리] mp3 폴더를 생성했습니다.
) else (
    echo [디렉토리] mp3 폴더가 이미 존재합니다.
)
echo.

REM Check if Python is installed
echo [시스템] Python 설치 상태를 확인하는 중...
python --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo [오류] Python이 설치되어 있지 않습니다.
    echo.
    echo Python 3.7 이상 버전이 필요합니다.
    echo 설치 주소: https://www.python.org/downloads/
    echo.
    echo 설치 후 다시 실행해주세요.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [확인] Python %PYTHON_VERSION% 발견
echo.

REM Check if required files exist
if not exist "audio_downloader.py" (
    echo [오류] audio_downloader.py 파일이 없습니다.
    pause
    exit /b 1
)

if not exist "gui_downloader.py" (
    echo [오류] gui_downloader.py 파일이 없습니다.
    pause
    exit /b 1
)

echo [설치] 필요한 패키지를 설치합니다...
echo.

REM Update pip first
echo [설치] pip 업데이트 중...
python -m pip install --upgrade pip --quiet

REM Install required packages
echo [설치] 기본 라이브러리 설치 중...
python -m pip install --quiet requests beautifulsoup4 tqdm lxml

echo [설치] 썸네일 처리 라이브러리 설치 중...
python -m pip install --quiet mutagen Pillow

if errorlevel 1 (
    echo.
    echo [오류] 패키지 설치에 실패했습니다.
    echo 인터넷 연결을 확인하고 다시 시도해주세요.
    echo.
    pause
    exit /b 1
)

echo.
echo [완료] 모든 패키지 설치가 완료되었습니다.
echo.
echo ================================================================
echo                       GUI 시작                              
echo ================================================================
echo.
echo [저장 위치] %CD%\mp3\
echo [핵심 기능] ASMR MP3 파일 다운로드
echo [사용 방법] URL을 복사하여 GUI 창에 붙여넣고 다운로드
echo [GUI 개선] 다운로드 정지 버튼으로 편리한 제어 가능
echo.
echo GUI 창이 열립니다...
echo.

REM Run the GUI with proper encoding
python gui_downloader.py

echo.
echo ================================================================
echo                       작업 완료                             
echo ================================================================
echo.
echo 다운로드된 파일은 mp3 폴더에서 확인할 수 있습니다.
echo MP3 파일에는 자동으로 앨범 아트가 추가되었습니다.
echo.
echo 프로그램을 종료하려면 아무 키나 누르세요...
pause > nul 