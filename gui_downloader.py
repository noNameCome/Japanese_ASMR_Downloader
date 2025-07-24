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
        self.root = tk.Tk()
        self.downloader = AudioDownloader()
        self.download_queue = queue.Queue()
        self.is_downloading = False
        self.stop_download = False
        
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
        
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        
    def setup_window(self) -> None:
        """Configure the main window."""
        self.root.title("🎵 Japanese ASMR Audio Downloader")
        self.root.geometry("900x700")
        self.root.minsize(700, 600)
        
        # Set window background to dark red
        self.root.configure(bg='#1a0d0d')
        
        # Set window icon (if available)
        try:
            # You can add an icon file here if you have one
            pass
        except:
            pass
            
        # Configure style with red theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom red/dark colors
        self.colors = {
            'bg_dark': '#1a0d0d',      # Very dark red background
            'bg_medium': '#2d1515',     # Medium dark red
            'bg_light': '#3d1f1f',      # Lighter dark red
            'primary': '#cc2936',       # Bright red
            'secondary': '#e74c3c',     # Orange-red
            'accent': '#ff6b6b',        # Light red/pink
            'success': '#27ae60',       # Green for success
            'warning': '#f39c12',       # Orange for warning
            'text_light': '#ffffff',    # White text
            'text_dark': '#2c3e50',     # Dark text
            'border': '#5d2c2c'         # Red border
        }
        
        # Configure custom styles
        
        # Frame styles
        style.configure('Dark.TFrame', 
                       background=self.colors['bg_dark'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Medium.TFrame', 
                       background=self.colors['bg_dark'],  # Changed to match main background
                       relief='flat',  # Changed from raised to flat
                       borderwidth=0)  # Removed border
        
        # Label styles - all using bg_dark to match window
        style.configure('Title.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['accent'],
                       font=('Helvetica', 18, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_light'],
                       font=('Helvetica', 11, 'bold'))
        
        style.configure('Info.TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_light'],
                       font=('Helvetica', 9))
        
        style.configure('Status.TLabel',
                       background=self.colors['bg_dark'],  # Changed to match background
                       foreground=self.colors['text_light'],
                       font=('Helvetica', 8),
                       relief='flat',  # Changed from sunken to flat
                       padding=(5, 2))
        
        # Button styles
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['text_light'],
                       font=('Helvetica', 10, 'bold'),
                       padding=(15, 8),
                       relief='raised',
                       borderwidth=2)
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['secondary']),
                            ('pressed', self.colors['accent'])])
        
        style.configure('Secondary.TButton',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_light'],
                       font=('Helvetica', 9),
                       padding=(10, 5),
                       relief='raised',
                       borderwidth=1)
        
        style.map('Secondary.TButton',
                 background=[('active', self.colors['border']),
                            ('pressed', self.colors['bg_medium'])])
        
        style.configure('Stop.TButton',
                       background=self.colors['warning'],
                       foreground=self.colors['text_dark'],
                       font=('Helvetica', 10, 'bold'),
                       padding=(15, 8),
                       relief='raised',
                       borderwidth=2)
        
        style.map('Stop.TButton',
                 background=[('active', '#e67e22'),
                            ('pressed', '#d35400')])
        
        # Progress bar style
        style.configure('Red.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['bg_light'],
                       borderwidth=1,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['secondary'])
        
        # Entry/Text widget styling (will be applied via configure)
        self.text_style = {
            'bg': '#2a1616',  # Slightly lighter than bg_dark for better readability
            'fg': self.colors['text_light'],
            'insertbackground': self.colors['accent'],
            'selectbackground': self.colors['primary'],
            'selectforeground': self.colors['text_light'],
            'relief': 'solid',
            'borderwidth': 1,
            'highlightthickness': 1,  # Reduced highlight thickness
            'highlightcolor': self.colors['accent'],
            'highlightbackground': self.colors['border']
        }
        
    def create_widgets(self) -> None:
        """Create and arrange GUI widgets."""
        # Main container with dark theme
        main_frame = ttk.Frame(self.root, padding="25", style='Dark.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title with enhanced styling
        title_label = ttk.Label(
            main_frame, 
            text="🎵 Japanese ASMR Audio Downloader",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25), sticky=tk.W)
        
        # URL input section with enhanced styling
        url_label = ttk.Label(main_frame, text="📎 웹페이지 URL (여러 URL을 각 줄에 입력):", style='Heading.TLabel')
        url_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))
        
        # Create frame for URL input with medium background
        url_container = ttk.Frame(main_frame, style='Dark.TFrame', padding="15")
        url_container.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        url_container.columnconfigure(0, weight=1)
        
        # URL text area with dark theme
        self.url_text = scrolledtext.ScrolledText(
            url_container,
            height=4,
            width=70,
            font=('Consolas', 10),
            wrap=tk.WORD,
            **self.text_style
        )
        self.url_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        
        # Button frame for URL controls
        url_button_frame = ttk.Frame(url_container, style='Dark.TFrame')
        url_button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Clear URL button with secondary style
        clear_btn = ttk.Button(
            url_button_frame,
            text="🗑️ Clear",
            command=self.clear_url,
            style='Secondary.TButton',
            width=12
        )
        clear_btn.grid(row=0, column=0, pady=(0, 10), padx=5)
        
        # Paste URL button with secondary style
        paste_btn = ttk.Button(
            url_button_frame,
            text="📋 Paste",
            command=self.paste_url,
            style='Secondary.TButton',
            width=12
        )
        paste_btn.grid(row=1, column=0, padx=5)
        
        # Action buttons container
        action_container = ttk.Frame(main_frame, style='Dark.TFrame', padding="20")
        action_container.grid(row=3, column=0, columnspan=3, pady=(0, 20))
        
        # Download button with primary style
        self.download_btn = ttk.Button(
            action_container,
            text="🚀 다운로드 시작",
            command=self.start_download,
            style='Primary.TButton'
        )
        self.download_btn.grid(row=0, column=0, padx=(0, 20), ipadx=10)
        
        # Stop button with warning style
        self.stop_btn = ttk.Button(
            action_container,
            text="⏹️ 정지",
            command=self.stop_download_process,
            style='Stop.TButton',
            state='disabled'
        )
        self.stop_btn.grid(row=0, column=1, ipadx=10)
        
        # Progress section with enhanced styling
        progress_container = ttk.Frame(main_frame, style='Dark.TFrame', padding="15")
        progress_container.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_container.columnconfigure(1, weight=1)
        
        progress_label = ttk.Label(progress_container, text="⚡ 진행 상황:", style='Heading.TLabel')
        progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="대기 중...")
        progress_status = ttk.Label(
            progress_container, 
            textvariable=self.progress_var,
            style='Info.TLabel'
        )
        progress_status.grid(row=0, column=1, sticky=tk.W, padx=(15, 0), pady=(0, 10))
        
        # Enhanced progress bar
        self.progress_bar = ttk.Progressbar(
            progress_container,
            mode='indeterminate',
            length=500,
            style='Red.Horizontal.TProgressbar'
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log output section with enhanced styling
        log_container = ttk.Frame(main_frame, style='Dark.TFrame', padding="15")
        log_container.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        log_label = ttk.Label(log_container, text="📋 실시간 로그:", style='Heading.TLabel')
        log_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Enhanced log text area
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            height=14,
            width=80,
            font=('Consolas', 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            **self.text_style
        )
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar with enhanced styling
        status_container = ttk.Frame(main_frame, style='Dark.TFrame')
        status_container.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        status_container.columnconfigure(1, weight=1)
        
        # Status icon and text
        status_icon = ttk.Label(status_container, text="🔴", style='Info.TLabel')
        status_icon.grid(row=0, column=0, padx=(10, 5))
        
        self.status_var = tk.StringVar(value="준비됨")
        status_bar = ttk.Label(
            status_container,
            textvariable=self.status_var,
            style='Status.TLabel'
        )
        status_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Version info
        version_label = ttk.Label(
            status_container,
            text="v2.0 Multi-URL Edition",
            style='Info.TLabel'
        )
        version_label.grid(row=0, column=2, padx=(0, 10))
        
    def setup_bindings(self) -> None:
        """Setup event bindings."""
        # Allow paste with Ctrl+V
        self.url_text.bind('<Control-v>', self.paste_url)
        self.url_text.bind('<Button-3>', self.show_context_menu)
        
        # Enter key to start download
        self.url_text.bind('<Return>', lambda e: self.start_download())
        
        # Close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def paste_url(self, event=None) -> None:
        """Handle URL paste."""
        try:
            clipboard = self.root.clipboard_get()
            if clipboard.startswith(('http://', 'https://')):
                # Clear the current content first to prevent duplication
                self.url_text.delete(1.0, tk.END)
                self.url_text.insert(tk.END, clipboard.strip())
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
        context_menu.add_command(label="전체 선택", command=lambda: self.url_text.select_range(1.0, tk.END))
        context_menu.add_command(label="지우기", command=self.clear_url)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def clear_url(self) -> None:
        """Clear the URL entry."""
        self.url_text.delete(1.0, tk.END)
        self.url_text.focus()
        
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
        urls = [line.strip() for line in self.url_text.get(1.0, tk.END).splitlines() if line.strip()]
        
        # Clean and validate URLs
        cleaned_urls = []
        invalid_urls = []
        
        for url in urls:
            cleaned_url = self.clean_url(url)
            if cleaned_url and cleaned_url.startswith(('http://', 'https://')):
                cleaned_urls.append(cleaned_url)
            elif cleaned_url:
                invalid_urls.append(cleaned_url)
        
        # Show validation results
        if invalid_urls:
            invalid_list = "\n".join(invalid_urls[:5])  # Show first 5 invalid URLs
            if len(invalid_urls) > 5:
                invalid_list += f"\n... 및 {len(invalid_urls) - 5}개 더"
            
            result = messagebox.askyesno(
                "유효하지 않은 URL 발견", 
                f"다음 {len(invalid_urls)}개의 URL이 유효하지 않습니다:\n\n{invalid_list}\n\n"
                f"유효한 {len(cleaned_urls)}개의 URL만 다운로드하시겠습니까?"
            )
            if not result:
                self.url_text.focus()
                return
        
        if not cleaned_urls:
            messagebox.showwarning("입력 오류", "다운로드할 유효한 URL을 입력해주세요.\n\nURL은 http:// 또는 https://로 시작해야 합니다.")
            self.url_text.focus()
            return
        
        # Check if already downloading
        if self.is_downloading:
            messagebox.showinfo("다운로드 중", "이미 다운로드가 진행 중입니다.")
            return
            
        # Update URL field with cleaned URLs
        self.url_text.delete(1.0, tk.END)
        for url in cleaned_urls:
            self.url_text.insert(tk.END, url + "\n")
            
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
            args=(cleaned_urls, str(self.auto_download_dir)),
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
        
    def download_worker(self, urls: list[str], output_dir: str) -> None:
        """Worker function for downloading in separate thread."""
        try:
            # Reset stop flag
            self.stop_download = False
            
            # Update status
            self.update_status("분석 중...")
            self.update_progress("웹페이지 분석 중...")
            
            self.log_message(f"총 {len(urls)}개의 URL을 순차적으로 처리합니다...")
            self.log_message("")
            
            total_success_count = 0
            total_file_count = 0
            
            # Process each URL sequentially
            for url_index, url in enumerate(urls, 1):
                # Check for stop signal
                if self.stop_download:
                    break
                
                self.log_message(f"🔗 [{url_index}/{len(urls)}] URL 처리 중: {url}")
                self.update_progress(f"URL {url_index}/{len(urls)} 분석 중...")
                
                try:
                    # Establish session for each URL
                    self.log_message("세션 설정 중...")
                    self.downloader.establish_session(url)
                    self.log_message("✓ 세션 설정 완료")
                    
                    # Check for stop signal
                    if self.stop_download:
                        break
                    
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
                            break
                        else:
                            # Handle other ValueError (like "No audio URLs found")
                            self.log_message(f"⚠ URL 추출 오류: {str(e)}")
                            self.log_message(f"❌ URL {url_index} 건너뛰기")
                            self.log_message("")
                            continue
                    except Exception as e:
                        # Handle any other unexpected errors
                        self.log_message(f"✗ 예상치 못한 오류: {str(e)}")
                        self.log_message(f"❌ URL {url_index} 건너뛰기")
                        self.log_message("")
                        continue
                    
                    # Check for stop signal
                    if self.stop_download:
                        break
                    
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
                        self.log_message(f"❌ URL {url_index} 건너뛰기")
                        self.log_message("")
                        continue
                    
                    # Check for stop signal
                    if self.stop_download:
                        break
                    
                    # Download files for this URL
                    url_success_count = 0
                    
                    for i, (audio_url, format_type) in enumerate(unique_audio_urls):
                        # Check for stop signal before each download
                        if self.stop_download:
                            break
                        
                        # Generate filename with URL index for multiple URLs
                        if len(urls) > 1:
                            filename = f"{base_title}_URL{url_index}"
                            if len(unique_audio_urls) > 1:
                                filename += f"_{i+1}"
                            filename += f".{format_type}"
                        else:
                            if len(unique_audio_urls) > 1:
                                filename = f"{base_title}_{i+1}.{format_type}"
                            else:
                                filename = f"{base_title}.{format_type}"
                        
                        filepath = os.path.join(output_dir, filename)
                        
                        self.log_message("")
                        self.log_message(f"[URL {url_index}: {i+1}/{len(unique_audio_urls)}] {format_type.upper()} 다운로드 시작: {filename}")
                        self.update_progress(f"URL {url_index}/{len(urls)}: 파일 {i+1}/{len(unique_audio_urls)} 다운로드 중...")
                        
                        success = False
                        
                        # Method 1: Standard download
                        if self.download_file_gui(audio_url, filepath, url):
                            success = True
                            url_success_count += 1
                            total_success_count += 1
                            self.log_message(f"✓ {format_type.upper()} 다운로드 완료!")
                        else:
                            # Check for stop signal
                            if self.stop_download:
                                break
                                
                            self.log_message(f"첫 번째 방법 실패, 대안 방법 시도 중...")
                            
                            # Method 2: Alternative download
                            if self.download_file_alternative_gui(audio_url, filepath, url):
                                success = True
                                url_success_count += 1
                                total_success_count += 1
                                self.log_message(f"✓ 대안 방법으로 {format_type.upper()} 다운로드 완료!")
                            else:
                                # Check for stop signal
                                if self.stop_download:
                                    break
                                    
                                self.log_message(f"대안 방법 실패, 브라우저 시뮬레이션 시도 중...")
                                
                                # Method 3: Browser simulation
                                if self.download_file_browser_sim_gui(audio_url, filepath, url):
                                    success = True
                                    url_success_count += 1
                                    total_success_count += 1
                                    self.log_message(f"✓ 브라우저 시뮬레이션으로 {format_type.upper()} 다운로드 완료!")
                                else:
                                    self.log_message(f"✗ 모든 방법으로 {format_type.upper()} 다운로드 실패")
                        
                        total_file_count += 1
                        self.log_message("")
                    
                    # Check for stop signal after processing this URL
                    if self.stop_download:
                        break
                    
                    # Summary for this URL
                    self.log_message(f"📊 URL {url_index} 완료: {url_success_count}/{len(unique_audio_urls)}개 파일 성공")
                    self.log_message("")
                    
                except Exception as e:
                    # Handle any unexpected errors for this URL
                    self.log_message(f"✗ URL {url_index} 처리 중 오류: {str(e)}")
                    self.log_message(f"❌ URL {url_index} 건너뛰기")
                    self.log_message("")
                    continue
            
            # Final status update
            if total_success_count > 0:
                self.log_message(f"🎉 전체 다운로드 완료!")
                self.log_message(f"📊 최종 결과: {total_success_count}/{total_file_count}개 파일 성공")
                self.log_message(f"💾 저장 위치: {output_dir}")
                
                self.update_progress(f"완료! {total_success_count}개 파일")
                self.update_status(f"다운로드 완료: {total_success_count}개 파일")
                
                # Show completion dialog
                messagebox.showinfo(
                    "다운로드 완료", 
                    f"{len(urls)}개 URL 처리 완료!\n\n"
                    f"성공한 파일: {total_success_count}개\n"
                    f"총 파일: {total_file_count}개\n\n"
                    f"저장 위치: {output_dir}"
                )
            else:
                self.log_message("✗ 모든 다운로드 실패")
                self.update_progress("실패")
                self.update_status("다운로드 실패")
                messagebox.showerror("다운로드 실패", "모든 파일 다운로드에 실패했습니다.")
            
        except Exception as e:
            # Handle any unexpected errors that weren't caught above
            error_msg = str(e)
            self.log_message(f"✗ 예상치 못한 전체 오류 발생: {error_msg}")
            
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
            self.download_btn.config(text="🚀 다운로드 시작")
            
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
                # Check if URL text area is empty
                current_text = self.url_text.get(1.0, tk.END).strip()
                if not current_text:
                    self.url_text.insert(tk.END, clipboard.strip() + "\n")
                    self.log_message(f"📋 클립보드에서 URL 자동 감지: {clipboard[:50]}...")
                else:
                    self.log_message(f"📋 클립보드에 URL이 있습니다: {clipboard[:50]}... (Paste 버튼으로 추가 가능)")
                # Do NOT auto-start download - just set the URL
        except Exception:
            pass  # Ignore clipboard errors
        
        # Focus on URL entry
        self.url_text.focus()
        
        # Start main loop
        self.root.mainloop()


def main() -> None:
    """Main function to run the GUI application."""
    try:
        app = AudioDownloaderGUI()
        app.run()
    except Exception as e:
        print(f"GUI 시작 오류: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main() 