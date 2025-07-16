#!/usr/bin/env python3
"""
Japanese ASMR Audio Downloader - GUI Version

A modern GUI interface for downloading MP3/M4A files from japaneseasmr.com
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import queue
from typing import Optional

# Import our existing downloader
from audio_downloader import AudioDownloader


class AudioDownloaderGUI:
    """Modern GUI for Japanese ASMR Audio Downloader."""
    
    def __init__(self) -> None:
        """Initialize the GUI application."""
        print("  - Tkinter 윈도우 생성 중...")
        self.root = tk.Tk()
        
        print("  - AudioDownloader 인스턴스 생성 중...")
        self.downloader = AudioDownloader()
        
        print("  - 큐 및 변수 초기화 중...")
        self.download_queue = queue.Queue()
        self.is_downloading = False
        self.stop_download = False
        
        print("  - 다운로드 디렉토리 설정 중...")
        # Set automatic download directory
        # Handle both script and EXE execution
        if getattr(sys, 'frozen', False):
            # Running as EXE
            exe_dir = Path(sys.executable).parent
            self.auto_download_dir = exe_dir / "mp3"
        else:
            # Running as script
            self.auto_download_dir = Path(__file__).parent / "mp3"
        
        self.auto_download_dir.mkdir(exist_ok=True)
        print(f"    → 다운로드 디렉토리: {self.auto_download_dir}")
        
        print("  - 윈도우 설정 중...")
        self.setup_window()
        
        print("  - 위젯 생성 중...")
        self.create_widgets()
        
        print("  - 이벤트 바인딩 설정 중...")
        self.setup_bindings()
        
    def setup_window(self) -> None:
        """Configure the main window."""
        self.root.title("🎵 Japanese ASMR Audio Downloader")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Set window icon (if available)
        try:
            # You can add an icon file here if you have one
            pass
        except:
            pass
            
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#F18F01',
            'background': '#F5F5F5',
            'text': '#2D3748'
        }
        
    def create_widgets(self) -> None:
        """Create and arrange GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🎵 Japanese ASMR Audio Downloader",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # URL input section
        url_label = ttk.Label(main_frame, text="웹페이지 URL:", font=('Helvetica', 10, 'bold'))
        url_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(
            main_frame, 
            textvariable=self.url_var,
            font=('Helvetica', 10),
            width=60
        )
        self.url_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Clear URL button
        clear_btn = ttk.Button(
            main_frame,
            text="Clear",
            command=self.clear_url,
            width=8
        )
        clear_btn.grid(row=2, column=2, padx=(10, 0), pady=(0, 15))
        
        # Button frame for download and stop buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Download button
        self.download_btn = ttk.Button(
            button_frame,
            text="🔽 다운로드 시작",
            command=self.start_download,
            style='Accent.TButton'
        )
        self.download_btn.grid(row=0, column=0, padx=(0, 10), ipadx=20, ipady=10)
        
        # Stop button
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹ 정지",
            command=self.stop_download_process,
            state='disabled'
        )
        self.stop_btn.grid(row=0, column=1, ipadx=20, ipady=10)
        
        # Progress section
        progress_label = ttk.Label(main_frame, text="진행 상황:", font=('Helvetica', 10, 'bold'))
        progress_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.progress_var = tk.StringVar(value="대기 중...")
        progress_status = ttk.Label(
            main_frame, 
            textvariable=self.progress_var,
            font=('Helvetica', 9)
        )
        progress_status.grid(row=4, column=1, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Log output section
        log_label = ttk.Label(main_frame, text="로그:", font=('Helvetica', 10, 'bold'))
        log_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        # Create frame for log and scrollbar
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            width=70,
            font=('Consolas', 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="준비됨")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            font=('Helvetica', 8)
        )
        status_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_bindings(self) -> None:
        """Setup event bindings."""
        # Allow paste with Ctrl+V
        self.url_entry.bind('<Control-v>', self.paste_url)
        self.url_entry.bind('<Button-3>', self.show_context_menu)
        
        # Enter key to start download
        self.url_entry.bind('<Return>', lambda e: self.start_download())
        
        # Close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def paste_url(self, event=None) -> None:
        """Handle URL paste."""
        try:
            clipboard = self.root.clipboard_get()
            if clipboard.startswith(('http://', 'https://')):
                # Clear the current content first to prevent duplication
                self.url_var.set("")
                self.url_var.set(clipboard.strip())
                self.log_message(f"URL 붙여넣기 완료: {clipboard[:50]}...")
                # Return "break" to prevent default tkinter paste behavior
                return "break"
        except Exception as e:
            self.log_message(f"붙여넣기 오류: {str(e)}")
        return "break"  # Always prevent default paste behavior
            
    def show_context_menu(self, event) -> None:
        """Show context menu for URL entry."""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="붙여넣기", command=self.paste_url)
        context_menu.add_command(label="전체 선택", command=lambda: self.url_entry.select_range(0, tk.END))
        context_menu.add_command(label="지우기", command=self.clear_url)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def clear_url(self) -> None:
        """Clear the URL entry."""
        self.url_var.set("")
        self.url_entry.focus()
        
    def log_message(self, message: str) -> None:
        """Add message to log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, status: str) -> None:
        """Update status bar."""
        self.status_var.set(status)
        self.root.update_idletasks()
        
    def update_progress(self, text: str) -> None:
        """Update progress text."""
        self.progress_var.set(text)
        self.root.update_idletasks()
        
    def start_download(self) -> None:
        """Start the download process."""
        url = self.url_var.get().strip()
        
        # Clean and validate URL
        url = self.clean_url(url)
        
        # Validation
        if not url:
            messagebox.showwarning("입력 오류", "URL을 입력해주세요.")
            self.url_entry.focus()
            return
            
        if not url.startswith(('http://', 'https://')):
            messagebox.showwarning("URL 오류", "올바른 HTTP/HTTPS URL을 입력해주세요.")
            self.url_entry.focus()
            return
            
        # Check if already downloading
        if self.is_downloading:
            messagebox.showinfo("다운로드 중", "이미 다운로드가 진행 중입니다.")
            return
            
        # Update URL field with cleaned URL
        self.url_var.set(url)
            
        # Start download in separate thread
        self.is_downloading = True
        self.stop_download = False
        self.download_btn.config(state='disabled', text="다운로드 중...")
        self.stop_btn.config(state='normal')
        self.progress_bar.start(10)
        self.update_progress("다운로드 준비 중...")
        self.update_status("다운로드 중...")
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Start download thread
        download_thread = threading.Thread(
            target=self.download_worker,
            args=(url, str(self.auto_download_dir)),
            daemon=True
        )
        download_thread.start()
        
    def stop_download_process(self) -> None:
        """Stop the download process."""
        if self.is_downloading:
            self.stop_download = True
            self.log_message("⏹ 사용자가 다운로드를 중지했습니다.")
            self.update_progress("다운로드 중지 중...")
            self.update_status("중지 중...")
            self.stop_btn.config(state='disabled')

    def clean_url(self, url: str) -> str:
        """Clean and validate URL to prevent duplication."""
        if not url:
            return ""
            
        # Remove leading/trailing whitespace
        url = url.strip()
        
        # Check for URL duplication (e.g., https://example.com/https://example.com/)
        if url.count('://') > 1:
            # Find the first occurrence of a valid URL
            if url.startswith('http://'):
                # Find the next occurrence of http:// or https://
                next_http = url.find('http://', 7)
                next_https = url.find('https://', 7)
                if next_http != -1 or next_https != -1:
                    # Take the later URL (which is likely the intended one)
                    if next_https != -1:
                        url = url[next_https:]
                    elif next_http != -1:
                        url = url[next_http:]
            elif url.startswith('https://'):
                # Find the next occurrence of http:// or https://
                next_http = url.find('http://', 8)
                next_https = url.find('https://', 8)
                if next_http != -1 or next_https != -1:
                    # Take the later URL (which is likely the intended one)
                    if next_https != -1:
                        url = url[next_https:]
                    elif next_http != -1:
                        url = url[next_http:]
        
        return url
        
    def download_worker(self, url: str, output_dir: str) -> None:
        """Worker function for downloading in separate thread."""
        try:
            # Reset stop flag
            self.stop_download = False
            
            # Update status
            self.update_status("분석 중...")
            self.update_progress("웹페이지 분석 중...")
            
            # Check for stop signal
            if self.stop_download:
                return
            
            # Establish session
            self.log_message("세션 설정 중...")
            self.downloader.establish_session(url)
            self.log_message("✓ 세션 설정 완료")
            
            # Check for stop signal
            if self.stop_download:
                return
            
            # Extract audio URLs
            self.log_message("오디오 URL 추출 중...")
            
            # Create stop callback function
            def stop_callback():
                return self.stop_download
            
            try:
                audio_urls = self.downloader.extract_audio_urls(url, stop_callback)
                self.log_message(f"발견된 오디오 소스: {len(audio_urls)}개")
            except ValueError as e:
                if "stopped by user" in str(e).lower():
                    self.log_message("🛑 사용자에 의해 URL 추출이 중단되었습니다.")
                    return
                else:
                    # Handle other ValueError (like "No audio URLs found")
                    self.log_message(f"⚠ URL 추출 오류: {str(e)}")
                    self.update_progress("URL 추출 실패")
                    self.update_status("URL 추출 실패")
                    messagebox.showerror("URL 추출 실패", f"오디오 URL을 찾을 수 없습니다:\n{str(e)}")
                    return
            except Exception as e:
                # Handle any other unexpected errors
                self.log_message(f"✗ 예상치 못한 오류: {str(e)}")
                self.update_progress("URL 추출 오류")
                self.update_status("URL 추출 오류")
                messagebox.showerror("오류", f"URL 추출 중 오류가 발생했습니다:\n{str(e)}")
                return
            
            # Check for stop signal
            if self.stop_download:
                return
            
            # Extract title for filename
            base_title = self.downloader.extract_title(url)
            self.log_message(f"제목: {base_title}")
            
            # Remove duplicates and filter for MP3 only
            seen_urls = set()
            unique_audio_urls = []
            for audio_url, format_type in audio_urls:
                if audio_url not in seen_urls and format_type.lower() == 'mp3':
                    seen_urls.add(audio_url)
                    unique_audio_urls.append((audio_url, format_type))
            
            self.log_message(f"✓ 발견된 전체 파일: {len(audio_urls)}개")
            self.log_message(f"✓ MP3 파일만 필터링: {len(unique_audio_urls)}개")
            
            if len(unique_audio_urls) == 0:
                self.log_message("⚠ MP3 파일을 찾을 수 없습니다.")
                self.update_progress("MP3 파일 없음")
                self.update_status("MP3 파일 없음")
                messagebox.showwarning("파일 없음", "다운로드할 MP3 파일을 찾을 수 없습니다.")
                return
            
            # Check for stop signal
            if self.stop_download:
                return

            # Download files
            success_count = 0
            
            for i, (audio_url, format_type) in enumerate(unique_audio_urls):
                # Check for stop signal before each download
                if self.stop_download:
                    self.log_message("⚠ 사용자에 의해 다운로드가 중단되었습니다.")
                    return
                
                # Generate filename
                if len(unique_audio_urls) > 1:
                    filename = f"{base_title}_{i+1}.{format_type}"
                else:
                    filename = f"{base_title}.{format_type}"
                
                filepath = os.path.join(output_dir, filename)
                
                self.log_message("")
                self.log_message(f"[{i+1}/{len(unique_audio_urls)}] {format_type.upper()} 다운로드 시작: {filename}")
                
                success = False
                
                # Method 1: Standard download
                if self.download_file_gui(audio_url, filepath, url):
                    success = True
                    success_count += 1
                    self.log_message(f"✓ {format_type.upper()} 다운로드 완료!")
                else:
                    # Check for stop signal
                    if self.stop_download:
                        return
                        
                    self.log_message(f"첫 번째 방법 실패, 대안 방법 시도 중...")
                    
                    # Method 2: Alternative download
                    if self.download_file_alternative_gui(audio_url, filepath, url):
                        success = True
                        success_count += 1
                        self.log_message(f"✓ 대안 방법으로 {format_type.upper()} 다운로드 완료!")
                    else:
                        # Check for stop signal
                        if self.stop_download:
                            return
                            
                        self.log_message(f"대안 방법 실패, 브라우저 시뮬레이션 시도 중...")
                        
                        # Method 3: Browser simulation
                        if self.download_file_browser_sim_gui(audio_url, filepath, url):
                            success = True
                            success_count += 1
                            self.log_message(f"✓ 브라우저 시뮬레이션으로 {format_type.upper()} 다운로드 완료!")
                        else:
                            self.log_message(f"✗ 모든 방법으로 {format_type.upper()} 다운로드 실패")
                
                self.log_message("")
            
            # Final status update
            if success_count > 0:
                self.log_message(f"다운로드 완료! 성공: {success_count}/{len(unique_audio_urls)}")
                self.update_progress(f"완료! {success_count}개 파일")
                self.update_status(f"다운로드 완료: {success_count}개 파일")
                
                # Show completion dialog
                messagebox.showinfo(
                    "다운로드 완료", 
                    f"{success_count}개의 파일이 성공적으로 다운로드되었습니다!\n\n저장 위치: {output_dir}"
                )
            else:
                self.log_message("✗ 모든 다운로드 실패")
                self.update_progress("실패")
                self.update_status("다운로드 실패")
                messagebox.showerror("다운로드 실패", "모든 파일 다운로드에 실패했습니다.")
            
        except Exception as e:
            # Handle any unexpected errors that weren't caught above
            error_msg = str(e)
            self.log_message(f"✗ 예상치 못한 오류 발생: {error_msg}")
            
            # Don't show error dialog if user stopped the download
            if not self.stop_download and "stopped by user" not in error_msg.lower():
                self.update_progress("오류 발생")
                self.update_status("오류 발생")
                messagebox.showerror("오류", f"다운로드 중 예상치 못한 오류가 발생했습니다:\n{error_msg}")
            elif self.stop_download:
                self.log_message("🛑 사용자에 의해 다운로드가 중단되었습니다.")
        
        finally:
            # Re-enable buttons
            self.download_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.is_downloading = False
            
            # Reset download button text
            self.download_btn.config(text="🔽 다운로드 시작")
            
            # Stop progress bar animation
            self.progress_bar.stop()
            
            # Reset progress bar mode to indeterminate
            self.progress_bar.config(mode='indeterminate')
            
            # Update status to ready if not stopped by user
            if not self.stop_download:
                self.update_progress("대기 중...")
                self.update_status("준비됨")
            else:
                self.update_progress("중단됨")
                self.update_status("사용자 중단")
            
            # Reset stop flag
            self.stop_download = False
            
    def download_file_gui(self, url: str, filename: str, page_url: str) -> bool:
        """GUI version of download_file with progress reporting."""
        try:
            import os
            import requests
            
            # Check for stop signal
            if self.stop_download:
                return False
            
            # Check if file already exists
            if os.path.exists(filename):
                self.log_message(f"파일이 이미 존재합니다: {os.path.basename(filename)}")
                return True
            
            self.log_message(f"다운로드 시작: {os.path.basename(filename)}")
            
            # Prepare headers for file download
            download_headers = self.downloader.get_random_headers()
            if page_url:
                download_headers['Referer'] = page_url
                download_headers['Origin'] = '/'.join(page_url.split('/')[:3])
            
            # Get file size for progress bar
            try:
                head_response = self.downloader.session.head(url, headers=download_headers, timeout=30)
                total_size = int(head_response.headers.get('content-length', 0))
            except:
                total_size = 0
            
            # Set progress bar to determinate mode for actual progress
            self.progress_bar.config(mode='determinate')
            self.progress_bar['maximum'] = 100
            
            # Download with progress
            response = self.downloader.session.get(url, headers=download_headers, stream=True, timeout=30)
            response.raise_for_status()
            
            downloaded = 0
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    # Check for stop signal
                    if self.stop_download:
                        if os.path.exists(filename):
                            os.remove(filename)  # Remove partial file
                        return False
                        
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        if total_size > 0:
                            progress_percent = (downloaded / total_size) * 100
                            self.progress_bar['value'] = progress_percent
                            self.update_progress(f"다운로드 중: {progress_percent:.1f}% ({downloaded//1024//1024}MB/{total_size//1024//1024}MB)")
                        else:
                            self.update_progress(f"다운로드 중: {downloaded//1024//1024}MB")
                        
                        self.root.update_idletasks()
            
            # Reset progress bar to indeterminate
            self.progress_bar.config(mode='indeterminate')
            self.log_message(f"✓ 다운로드 완료: {os.path.basename(filename)}")
            return True
            
        except Exception as e:
            # Reset progress bar to indeterminate
            self.progress_bar.config(mode='indeterminate')
            # Clean up partial file if it exists
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass
            self.log_message(f"다운로드 오류: {str(e)}")
            return False
            
    def download_file_alternative_gui(self, url: str, filename: str, page_url: str) -> bool:
        """GUI version of alternative download with logging."""
        try:
            return self.downloader.download_file_alternative(url, filename, page_url)
        except Exception as e:
            self.log_message(f"대안 다운로드 오류: {str(e)}")
            return False
            
    def download_file_browser_sim_gui(self, url: str, filename: str, page_url: str) -> bool:
        """GUI version of browser simulation download with logging."""
        try:
            return self.downloader.download_file_browser_sim(url, filename, page_url)
        except Exception as e:
            self.log_message(f"브라우저 시뮬레이션 오류: {str(e)}")
            return False
            
    def on_closing(self) -> None:
        """Handle window closing."""
        if self.is_downloading:
            if messagebox.askokcancel("종료", "다운로드가 진행 중입니다. 정말 종료하시겠습니까?"):
                self.stop_download = True
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self) -> None:
        """Start the GUI application."""
        self.log_message("🎵 Japanese ASMR Audio Downloader GUI 시작됨")
        self.log_message("URL을 입력하고 다운로드 버튼을 클릭하세요.")
        self.log_message("")
        
        # Check clipboard for URL automatically
        try:
            clipboard = self.root.clipboard_get()
            if clipboard and clipboard.startswith(('http://', 'https://')):
                self.url_var.set(clipboard.strip())
                self.log_message(f"📋 클립보드에서 URL 자동 감지: {clipboard[:50]}...")
                # Do NOT auto-start download - just set the URL
        except Exception:
            pass  # Ignore clipboard errors
        
        # Focus on URL entry
        self.url_entry.focus()
        
        # Start main loop
        self.root.mainloop()


def main() -> None:
    """Main function to run the GUI application."""
    print("🔍 GUI 디버깅 시작...")
    
    try:
        print("1. AudioDownloaderGUI 클래스 초기화 중...")
        app = AudioDownloaderGUI()
        print("✓ GUI 초기화 완료")
        
        print("2. GUI 실행 중...")
        app.run()
        print("✓ GUI 정상 종료")
        
    except ImportError as e:
        print(f"❌ 모듈 import 오류: {e}")
        print("필요한 패키지가 설치되어 있는지 확인하세요:")
        print("- tkinter (Python 기본 제공)")
        print("- requests")
        print("- beautifulsoup4")
        print("- tqdm")
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ GUI 시작 오류: {e}")
        import traceback
        print("상세 오류 정보:")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main() 