
<img width="1487" height="632" alt="image" src="https://github.com/user-attachments/assets/53f9844b-5978-4568-9cfc-9279aef760b0" />


# Japanese ASMR Downloader

---

## 🚀 빠른 시작

1.  `Japanese_ASMR_Downloader.bat` 실행
2.  패키지 자동 설치 대기
3.  GUI에서 URL 입력 후 다운로드
4.  `mp3` 폴더에서 파일 확인

---

## 📁 배포 패키지 구성

### ✅ 필수 파일들

* `Japanese_ASMR_Downloader.bat` ← 메인 실행 파일
* `audio_downloader.py` ← 핵심 다운로드 엔진
* `gui_downloader.py` ← GUI 인터페이스
* `requirements.txt` ← 의존성 패키지 목록
* `사용법_최종판.txt` ← 이 설명서

### 🗂️ 자동 생성 폴더

* `mp3/` ← 다운로드 파일 저장소

---

## 💻 시스템 요구사항

* **운영체제**: Windows 7/8/10/11 (64비트 권장)
* **Python**: 3.7 이상 버전 필요
* **네트워크**: 안정적인 인터넷 연결
* **용량**: 최소 100MB 여유 공간

---

## 📋 설치되는 패키지

### 핵심 라이브러리

* `requests` (HTTP 요청 처리)
* `beautifulsoup4` (HTML 파싱)
* `tqdm` (진행률 표시)
* `lxml` (XML 파서)

### 썸네일 기능

* `mutagen` (MP3 메타데이터 편집)
* `Pillow` (이미지 처리)

---

## 🔧 사용법 상세
**타겟 페이지**: `https://japaneseasmr.com/` (그 외 사이트 지원 불가)

**샘플 URL**:
* `https://japaneseasmr.com/134918/`
* `https://japaneseasmr.com/121293/`
* `https://japaneseasmr.com/12314/`

### 0단계: VPN 필수 사용

### 1단계: 프로그램 실행

* `Japanese_ASMR_Downloader.bat` 더블클릭
* 콘솔 창에서 자동 설치 과정 확인

### 2단계: URL 준비

* 브라우저에서 다운로드할 페이지 이동
* 주소창의 URL 전체 복사

### 3단계: GUI 사용

* URL 입력란에 붙여넣기 (Ctrl+V)
* "다운로드 시작" 버튼 클릭
* 진행 상황 모니터링

---

## ❗ 문제 해결 가이드

* **Q: "Python이 설치되어 있지 않습니다" 오류**
    * **A:** [https://python.org](https://python.org) 에서 Python 3.7+ 설치
* **Q: 패키지 설치 실패**
    * **A:** 관리자 권한으로 실행하거나 인터넷 연결 확인
* **Q: 한글이 깨져 보임**
    * **A:** 콘솔 폰트를 "굴림체" 또는 "맑은고딕"으로 변경
* **Q: GUI가 열리지 않음**
    * **A:** Python `tkinter` 패키지 확인 (보통 기본 설치됨)
* **Q: 다운로드 실패 (403 오류)**
    * **A:** 프로그램에 내장된 우회 기능이 자동 작동
* **Q: MP3 앨범 아트가 보이지 않음**
    * **A:** 플레이어 새로고침 또는 다른 플레이어 사용

---

## 📞 지원 및 문의

기술적 문의는 GitHub 저장소의 Issues 섹션을 이용해주세요. 프로그램 개선 제안도 환영합니다.
