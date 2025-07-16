#!/usr/bin/env python3
"""
Japanese ASMR Audio Downloader

This script downloads MP3/M4A files from japaneseasmr.com
by extracting direct audio URLs from the webpage HTML.
"""

import os
import re
import sys
import time
import random
from pathlib import Path
from typing import Optional, Tuple, List
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class AudioDownloader:
    """Audio downloader for Japanese ASMR website."""
    
    def __init__(self) -> None:
        """Initialize the downloader with session and headers."""
        self.session = requests.Session()
        
        # Multiple User-Agents to rotate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
    def get_random_headers(self) -> dict:
        """Get randomized headers to avoid detection."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://japaneseasmr.com/',
        }
        
    def extract_audio_urls(self, page_url: str, stop_callback=None) -> List[Tuple[str, str]]:
        """
        Extract audio URLs from the webpage.
        
        Args:
            page_url: URL of the webpage containing audio
            stop_callback: Optional callback function that returns True if download should stop
            
        Returns:
            List of tuples containing (url, format) pairs
            
        Raises:
            requests.RequestException: If unable to fetch the webpage
            ValueError: If no audio URLs found
        """
        response = None
        
        # First try: Standard request without bypass
        try:
            print("📡 기본 요청 시도 중...")
            response = self.session.get(page_url, timeout=30)
            
            if response.status_code == 200:
                print("✓ 기본 요청 성공!")
            elif response.status_code == 403:
                print("⚠ 403 차단 감지, 우회 방법 시도...")
                response = None  # Reset response to trigger bypass
            else:
                print(f"⚠ 응답 코드 {response.status_code}, 우회 방법 시도...")
                response = None  # Reset response to trigger bypass
                
        except Exception as e:
            print(f"⚠ 기본 요청 실패 ({e}), 우회 방법 시도...")
            response = None
        
        # If basic request failed, try bypass methods
        if not response or response.status_code != 200:
            # Enhanced 403 bypass system
            bypass_methods = [
                self._method_1_standard_request,
                self._method_2_mobile_headers,
                self._method_3_firefox_simulation,
                self._method_4_minimal_headers,
                self._method_5_session_rotation,
                self._method_6_proxy_style,
                self._method_7_stealth_mode
            ]
            
            for method_num, method in enumerate(bypass_methods, 1):
                # Check if stop was requested
                if stop_callback and stop_callback():
                    print("🛑 사용자에 의해 우회 시도가 중단되었습니다.")
                    raise ValueError("Download stopped by user during bypass attempt")
                    
                try:
                    print(f"⚠ 우회 방법 {method_num} 시도 중...")
                    response = method(page_url, stop_callback)
                    if response and response.status_code == 200:
                        print(f"✓ 우회 방법 {method_num} 성공!")
                        break
                        
                except requests.exceptions.HTTPError as e:
                    if stop_callback and stop_callback():
                        print("🛑 사용자에 의해 우회 시도가 중단되었습니다.")
                        raise ValueError("Download stopped by user during bypass attempt")
                        
                    if e.response and e.response.status_code == 403:
                        print(f"✗ 방법 {method_num} 실패 (403)")
                        continue
                    else:
                        print(f"✗ 방법 {method_num} 실패: {e}")
                        continue
                except Exception as e:
                    if stop_callback and stop_callback():
                        print("🛑 사용자에 의해 우회 시도가 중단되었습니다.")
                        raise ValueError("Download stopped by user during bypass attempt")
                        
                    print(f"✗ 방법 {method_num} 실패: {e}")
                    continue
        
        if not response or response.status_code != 200:
            raise requests.RequestException("모든 우회 방법이 실패했습니다. 사이트가 강화된 차단을 사용하고 있을 수 있습니다.")
            
        soup = BeautifulSoup(response.content, 'html.parser')
        audio_urls = []
        
        # Method 1: Look for audio sources in video elements
        video_elements = soup.find_all('video')
        for video in video_elements:
            sources = video.find_all('source')
            for source in sources:
                src = source.get('src')
                audio_type = source.get('type', '')
                
                if src and not src.startswith('blob:') and ('audio' in audio_type or src.endswith(('.mp3', '.m4a'))):
                    # Determine format from URL or type
                    if '.mp3' in src or 'audio/mpeg' in audio_type:
                        format_type = 'mp3'
                    elif '.m4a' in src or 'audio/mp4' in audio_type:
                        format_type = 'm4a'
                    else:
                        format_type = 'audio'
                    
                    audio_urls.append((src, format_type))
        
        # Method 2: Look for direct audio elements (excluding blob URLs)
        audio_elements = soup.find_all('audio')
        for audio in audio_elements:
            sources = audio.find_all('source')
            for source in sources:
                src = source.get('src')
                audio_type = source.get('type', '')
                
                if src and not src.startswith('blob:'):
                    if '.mp3' in src or 'audio/mpeg' in audio_type:
                        format_type = 'mp3'
                    elif '.m4a' in src or 'audio/mp4' in audio_type:
                        format_type = 'm4a'
                    else:
                        format_type = 'audio'
                    
                    audio_urls.append((src, format_type))
        
        # Method 3: Search for audio URLs in JavaScript code
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                script_content = script.string
                
                # Look for various patterns that might contain audio URLs
                import re
                
                # Pattern for direct audio file URLs
                audio_patterns = [
                    r'["\']([^"\']*\.mp3)["\']',
                    r'["\']([^"\']*\.m4a)["\']',
                    r'["\']([^"\']*audio[^"\']*\.mp3)["\']',
                    r'["\']([^"\']*audio[^"\']*\.m4a)["\']',
                    r'url["\s]*:["\s]*["\']([^"\']*\.mp3)["\']',
                    r'url["\s]*:["\s]*["\']([^"\']*\.m4a)["\']',
                    r'src["\s]*:["\s]*["\']([^"\']*\.mp3)["\']',
                    r'src["\s]*:["\s]*["\']([^"\']*\.m4a)["\']',
                    r'audioUrl["\s]*:["\s]*["\']([^"\']*\.mp3)["\']',
                    r'audioUrl["\s]*:["\s]*["\']([^"\']*\.m4a)["\']',
                ]
                
                for pattern in audio_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        if match and not match.startswith('blob:'):
                            # Make sure it's a valid URL
                            if match.startswith('http') or match.startswith('/'):
                                format_type = 'mp3' if '.mp3' in match.lower() else 'm4a'
                                
                                # Convert relative URLs to absolute
                                if match.startswith('/'):
                                    base_url = '/'.join(page_url.split('/')[:3])
                                    match = base_url + match
                                
                                audio_urls.append((match, format_type))
        
        # Method 4: Look for data attributes that might contain audio URLs
        all_elements = soup.find_all(attrs={'data-audio': True})
        for element in all_elements:
            audio_url = element.get('data-audio')
            if audio_url and not audio_url.startswith('blob:'):
                format_type = 'mp3' if '.mp3' in audio_url.lower() else 'm4a'
                if audio_url.startswith('/'):
                    base_url = '/'.join(page_url.split('/')[:3])
                    audio_url = base_url + audio_url
                audio_urls.append((audio_url, format_type))
        
        # Method 5: Look for common data attributes
        for attr in ['data-src', 'data-url', 'data-file', 'data-audio-url']:
            elements = soup.find_all(attrs={attr: True})
            for element in elements:
                url = element.get(attr)
                if url and (url.endswith('.mp3') or url.endswith('.m4a')) and not url.startswith('blob:'):
                    format_type = 'mp3' if '.mp3' in url.lower() else 'm4a'
                    if url.startswith('/'):
                        base_url = '/'.join(page_url.split('/')[:3])
                        url = base_url + url
                    audio_urls.append((url, format_type))
        
        # Method 6: Try to construct URLs based on page URL pattern
        # For japaneseasmr.com, try common patterns
        if 'japaneseasmr.com' in page_url and not audio_urls:
            print("⚠ blob URL 감지 - 파일 패턴 추측 중...")
            
            # Extract post ID from URL
            url_parts = page_url.rstrip('/').split('/')
            post_id = None
            
            for part in reversed(url_parts):
                if part.isdigit():
                    post_id = part
                    break
            
            if post_id:
                # Try common file patterns for this site
                base_domain = '/'.join(page_url.split('/')[:3])
                
                potential_patterns = [
                    f"{base_domain}/audio/{post_id}.mp3",
                    f"{base_domain}/audio/{post_id}.m4a",
                    f"{base_domain}/files/{post_id}.mp3",
                    f"{base_domain}/files/{post_id}.m4a",
                    f"{base_domain}/media/{post_id}.mp3",
                    f"{base_domain}/media/{post_id}.m4a",
                    f"{base_domain}/uploads/{post_id}.mp3",
                    f"{base_domain}/uploads/{post_id}.m4a",
                    f"{base_domain}/content/{post_id}.mp3",
                    f"{base_domain}/content/{post_id}.m4a",
                    # Additional patterns for this specific site
                    f"{base_domain}/wp-content/uploads/{post_id}.mp3",
                    f"{base_domain}/wp-content/uploads/{post_id}.m4a",
                    f"{base_domain}/wp-content/uploads/audio/{post_id}.mp3",
                    f"{base_domain}/wp-content/uploads/audio/{post_id}.m4a",
                    f"{base_domain}/downloads/{post_id}.mp3",
                    f"{base_domain}/downloads/{post_id}.m4a",
                    f"{base_domain}/assets/audio/{post_id}.mp3",
                    f"{base_domain}/assets/audio/{post_id}.m4a",
                    f"{base_domain}/static/audio/{post_id}.mp3",
                    f"{base_domain}/static/audio/{post_id}.m4a",
                    # Try with different file naming patterns
                    f"{base_domain}/audio/audio_{post_id}.mp3",
                    f"{base_domain}/audio/audio_{post_id}.m4a",
                    f"{base_domain}/files/file_{post_id}.mp3",
                    f"{base_domain}/files/file_{post_id}.m4a",
                    # Try with padded IDs
                    f"{base_domain}/audio/{post_id.zfill(6)}.mp3",
                    f"{base_domain}/audio/{post_id.zfill(6)}.m4a",
                    f"{base_domain}/files/{post_id.zfill(6)}.mp3",
                    f"{base_domain}/files/{post_id.zfill(6)}.m4a",
                ]
                
                # Test each potential URL with bypass headers
                for test_url in potential_patterns:
                    try:
                        print(f"  테스트 중: {test_url}")
                        # Use the successful bypass headers from above
                        headers = self.get_random_headers()
                        head_response = self.session.head(test_url, headers=headers, timeout=10)
                        if head_response.status_code == 200:
                            format_type = 'mp3' if '.mp3' in test_url else 'm4a'
                            audio_urls.append((test_url, format_type))
                            print(f"  ✓ 발견: {test_url}")
                            break
                    except:
                        continue
        
        # Method 6.5: Advanced JavaScript analysis for blob URL sites
        if 'japaneseasmr.com' in page_url and not audio_urls:
            print("⚠ 고급 JavaScript 분석 시도 중...")
            
            # Look for patterns that might reveal actual file URLs
            script_patterns = [
                r'audioUrl["\s]*:["\s]*["\']([^"\']*\.mp3)["\']',
                r'audioUrl["\s]*:["\s]*["\']([^"\']*\.m4a)["\']',
                r'src["\s]*:["\s]*["\']([^"\']*\.mp3)["\']',
                r'src["\s]*:["\s]*["\']([^"\']*\.m4a)["\']',
                r'file["\s]*:["\s]*["\']([^"\']*\.mp3)["\']',
                r'file["\s]*:["\s]*["\']([^"\']*\.m4a)["\']',
                r'audio["\s]*:["\s]*["\']([^"\']*\.mp3)["\']',
                r'audio["\s]*:["\s]*["\']([^"\']*\.m4a)["\']',
                r'url["\s]*=["\s]*["\']([^"\']*\.mp3)["\']',
                r'url["\s]*=["\s]*["\']([^"\']*\.m4a)["\']',
                # Look for direct file references in variable assignments
                r'var\s+\w+\s*=\s*["\']([^"\']*\.mp3)["\']',
                r'var\s+\w+\s*=\s*["\']([^"\']*\.m4a)["\']',
                r'let\s+\w+\s*=\s*["\']([^"\']*\.mp3)["\']',
                r'let\s+\w+\s*=\s*["\']([^"\']*\.m4a)["\']',
                r'const\s+\w+\s*=\s*["\']([^"\']*\.mp3)["\']',
                r'const\s+\w+\s*=\s*["\']([^"\']*\.m4a)["\']',
                # WordPress media library patterns
                r'wp-content/uploads/[^"\']*\.mp3',
                r'wp-content/uploads/[^"\']*\.m4a',
            ]
            
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    for pattern in script_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        for match in matches:
                            if match and not match.startswith('blob:'):
                                # Make sure it's a valid URL
                                if match.startswith('http') or match.startswith('/'):
                                    format_type = 'mp3' if '.mp3' in match.lower() else 'm4a'
                                    
                                    # Convert relative URLs to absolute
                                    if match.startswith('/'):
                                        base_url = '/'.join(page_url.split('/')[:3])
                                        match = base_url + match
                                    
                                    # Verify the URL actually works with bypass headers
                                    try:
                                        print(f"  JS에서 발견된 URL 검증 중: {match}")
                                        headers = self.get_random_headers()
                                        head_response = self.session.head(match, headers=headers, timeout=10)
                                        if head_response.status_code == 200:
                                            audio_urls.append((match, format_type))
                                            print(f"  ✓ JS에서 유효한 URL 발견: {match}")
                                    except:
                                        continue

        # Method 6.7: Look for base64 encoded URLs or other encoded patterns
        if 'japaneseasmr.com' in page_url and not audio_urls:
            print("⚠ 인코딩된 URL 패턴 검색 중...")
            
            # Look for base64 patterns that might contain URLs
            import base64
            
            for script in script_tags:
                if script.string:
                    script_content = script.string
                    
                    # Look for base64 patterns
                    base64_patterns = re.findall(r'["\']([A-Za-z0-9+/]{20,}={0,2})["\']', script_content)
                    
                    for b64_string in base64_patterns:
                        try:
                            decoded = base64.b64decode(b64_string).decode('utf-8', errors='ignore')
                            if '.mp3' in decoded or '.m4a' in decoded:
                                # Extract potential URLs from decoded content
                                url_matches = re.findall(r'https?://[^\s"\'<>]+\.(?:mp3|m4a)', decoded)
                                for url_match in url_matches:
                                    format_type = 'mp3' if '.mp3' in url_match.lower() else 'm4a'
                                    print(f"  Base64에서 발견된 URL 검증 중: {url_match}")
                                    try:
                                        headers = self.get_random_headers()
                                        head_response = self.session.head(url_match, headers=headers, timeout=10)
                                        if head_response.status_code == 200:
                                            audio_urls.append((url_match, format_type))
                                            print(f"  ✓ Base64에서 유효한 URL 발견: {url_match}")
                                    except:
                                        continue
                        except:
                            continue

        # Method 6.8: Site-specific analysis for japaneseasmr.com
        if 'japaneseasmr.com' in page_url and not audio_urls:
            print("⚠ japaneseasmr.com 특화 분석 시도 중...")
            
            # Extract post ID from URL
            url_parts = page_url.rstrip('/').split('/')
            post_id = None
            
            for part in reversed(url_parts):
                if part.isdigit():
                    post_id = part
                    break
            
            if post_id:
                base_domain = '/'.join(page_url.split('/')[:3])
                
                # Try to find any form or AJAX endpoint that might reveal the file location
                forms = soup.find_all('form')
                for form in forms:
                    action = form.get('action', '')
                    if 'download' in action.lower() or 'audio' in action.lower():
                        print(f"  Form action 발견: {action}")
                
                # Look for any div or element with audio-related classes or IDs
                audio_containers = soup.find_all(['div', 'section', 'article'], 
                    class_=lambda x: x and any(keyword in x.lower() for keyword in ['audio', 'player', 'media', 'download']))
                
                for container in audio_containers:
                    # Look for data attributes that might contain file info
                    for attr_name in container.attrs:
                        if 'data' in attr_name.lower():
                            attr_value = container.attrs[attr_name]
                            if isinstance(attr_value, str) and (post_id in attr_value or '.mp3' in attr_value.lower() or '.m4a' in attr_value.lower()):
                                print(f"  Audio container에서 발견: {attr_name}={attr_value}")
                
                # Look for any hidden input fields that might contain file URLs
                hidden_inputs = soup.find_all('input', type='hidden')
                for hidden_input in hidden_inputs:
                    value = hidden_input.get('value', '')
                    if value and (post_id in value or '.mp3' in value.lower() or '.m4a' in value.lower()):
                        print(f"  Hidden input에서 발견: {hidden_input.get('name')}={value}")
                        
                        # If this looks like a URL, try to use it
                        if value.startswith(('http', '/')):
                            format_type = 'mp3' if '.mp3' in value.lower() else 'm4a'
                            if value.startswith('/'):
                                value = base_domain + value
                            
                            try:
                                print(f"  Hidden input URL 검증 중: {value}")
                                headers = self.get_random_headers()
                                head_response = self.session.head(value, headers=headers, timeout=10)
                                if head_response.status_code == 200:
                                    audio_urls.append((value, format_type))
                                    print(f"  ✓ Hidden input에서 유효한 URL 발견: {value}")
                            except:
                                continue
                
                # Try to make an AJAX-like request to common API endpoints with bypass headers
                api_endpoints = [
                    f"{base_domain}/wp-json/wp/v2/media?search={post_id}",
                    f"{base_domain}/api/audio/{post_id}",
                    f"{base_domain}/api/download/{post_id}",
                    f"{base_domain}/download.php?id={post_id}",
                    f"{base_domain}/get_audio.php?id={post_id}",
                ]
                
                for api_url in api_endpoints:
                    try:
                        print(f"  API 엔드포인트 시도: {api_url}")
                        headers = self.get_random_headers()
                        api_response = self.session.get(api_url, headers=headers, timeout=10)
                        if api_response.status_code == 200:
                            response_text = api_response.text
                            # Look for URLs in the API response
                            url_matches = re.findall(r'https?://[^\s"\'<>]+\.(?:mp3|m4a)', response_text)
                            for url_match in url_matches:
                                format_type = 'mp3' if '.mp3' in url_match.lower() else 'm4a'
                                audio_urls.append((url_match, format_type))
                                print(f"  ✓ API에서 URL 발견: {url_match}")
                    except:
                        continue
        
        # Method 6.9: Last resort - try direct file access with common naming patterns
        if 'japaneseasmr.com' in page_url and not audio_urls:
            print("⚠ 최후 수단 - 일반적인 파일명 패턴 시도 중...")
            
            url_parts = page_url.rstrip('/').split('/')
            post_id = None
            
            for part in reversed(url_parts):
                if part.isdigit():
                    post_id = part
                    break
            
            if post_id:
                base_domain = '/'.join(page_url.split('/')[:3])
                
                # Try even more file patterns based on common WordPress/CMS patterns
                last_resort_patterns = [
                    # WordPress uploads with year/month structure
                    f"{base_domain}/wp-content/uploads/2023/{post_id}.mp3",
                    f"{base_domain}/wp-content/uploads/2024/{post_id}.mp3",
                    f"{base_domain}/wp-content/uploads/2023/12/{post_id}.mp3",
                    f"{base_domain}/wp-content/uploads/2024/01/{post_id}.mp3",
                    # CDN or subdomain patterns
                    f"https://cdn.japaneseasmr.com/audio/{post_id}.mp3",
                    f"https://files.japaneseasmr.com/{post_id}.mp3",
                    f"https://media.japaneseasmr.com/{post_id}.mp3",
                    # Common file server patterns
                    f"{base_domain}/fileserver/{post_id}.mp3",
                    f"{base_domain}/storage/{post_id}.mp3",
                    f"{base_domain}/public/{post_id}.mp3",
                    # Try with different extensions
                    f"{base_domain}/audio/{post_id}.wav",
                    f"{base_domain}/audio/{post_id}.flac",
                ]
                
                for test_url in last_resort_patterns:
                    try:
                        print(f"  최후 패턴 테스트: {test_url}")
                        headers = self.get_random_headers()
                        head_response = self.session.head(test_url, headers=headers, timeout=5)
                        if head_response.status_code == 200:
                            # Determine format from URL
                            if '.mp3' in test_url:
                                format_type = 'mp3'
                            elif '.m4a' in test_url:
                                format_type = 'm4a'
                            elif '.wav' in test_url:
                                format_type = 'wav'
                            elif '.flac' in test_url:
                                format_type = 'flac'
                            else:
                                format_type = 'audio'
                            
                            audio_urls.append((test_url, format_type))
                            print(f"  ✓ 최후 패턴에서 발견: {test_url}")
                            break
                    except:
                        continue
        
        # Method 7: Look for any links to audio files in the entire page
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if href and (href.endswith('.mp3') or href.endswith('.m4a')):
                format_type = 'mp3' if '.mp3' in href.lower() else 'm4a'
                if href.startswith('/'):
                    base_url = '/'.join(page_url.split('/')[:3])
                    href = base_url + href
                audio_urls.append((href, format_type))
        
        if not audio_urls:
            raise ValueError("No audio URLs found on the webpage")
            
        return audio_urls
    
    def _method_1_standard_request(self, page_url: str, stop_callback=None) -> requests.Response:
        """Standard request with enhanced headers."""
        headers = self.get_random_headers()
        delay = random.uniform(0.2, 0.5)
        
        # Check for stop during delay
        for _ in range(int(delay * 10)):  # Check every 0.1 seconds
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
            time.sleep(0.1)
        
        return self.session.get(page_url, timeout=30, headers=headers)
    
    def _method_2_mobile_headers(self, page_url: str, stop_callback=None) -> requests.Response:
        """Mobile device simulation."""
        delay = random.uniform(0.2, 0.5)
        
        # Check for stop during delay
        for _ in range(int(delay * 10)):  # Check every 0.1 seconds
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
            time.sleep(0.1)
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://japaneseasmr.com/',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }
        return self.session.get(page_url, timeout=30, headers=headers)
    
    def _method_3_firefox_simulation(self, page_url: str, stop_callback=None) -> requests.Response:
        """Firefox browser simulation."""
        delay = random.uniform(0.2, 0.5)
        
        # Check for stop during delay
        for _ in range(int(delay * 10)):  # Check every 0.1 seconds
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
            time.sleep(0.1)
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Referer': 'https://japaneseasmr.com/',
        }
        return self.session.get(page_url, timeout=30, headers=headers)
    
    def _method_4_minimal_headers(self, page_url: str, stop_callback=None) -> requests.Response:
        """Minimal headers approach."""
        delay = random.uniform(0.2, 0.5)
        
        # Check for stop during delay
        for _ in range(int(delay * 10)):  # Check every 0.1 seconds
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
            time.sleep(0.1)
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        }
        return self.session.get(page_url, timeout=30, headers=headers)
    
    def _method_5_session_rotation(self, page_url: str, stop_callback=None) -> requests.Response:
        """Create new session with different configuration."""
        delay = random.uniform(0.2, 0.5)
        
        # Check for stop during delay
        for _ in range(int(delay * 10)):  # Check every 0.1 seconds
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
            time.sleep(0.1)
            
        new_session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        return new_session.get(page_url, timeout=30, headers=headers)
    
    def _method_6_proxy_style(self, page_url: str, stop_callback=None) -> requests.Response:
        """Proxy-like request with different approach."""
        delay = random.uniform(0.2, 0.5)
        
        # Check for stop during delay
        for _ in range(int(delay * 10)):  # Check every 0.1 seconds
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
            time.sleep(0.1)
        
        # Visit homepage first to establish session
        try:
            domain = '/'.join(page_url.split('/')[:3])
            self.session.get(domain, timeout=15)
            
            # Check for stop after first request
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
                
            time.sleep(0.2)  # Reduced delay
        except ValueError:
            raise  # Re-raise stop request
        except:
            pass
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Referer': 'https://google.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
        return self.session.get(page_url, timeout=30, headers=headers)
    
    def _method_7_stealth_mode(self, page_url: str, stop_callback=None) -> requests.Response:
        """Advanced stealth mode with multiple steps."""
        delay = random.uniform(0.2, 0.5)
        
        # Check for stop during delay
        for _ in range(int(delay * 10)):  # Check every 0.1 seconds
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
            time.sleep(0.1)
        
        # Create completely new session
        stealth_session = requests.Session()
        
        # Step 1: Visit main domain
        try:
            domain = '/'.join(page_url.split('/')[:3])
            basic_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9',
                'Connection': 'keep-alive',
            }
            stealth_session.get(domain, headers=basic_headers, timeout=15)
            
            # Check for stop after first request
            if stop_callback and stop_callback():
                raise ValueError("Download stopped by user")
                
            # Reduced delay with stop checking
            delay = random.uniform(0.1, 0.3)
            for _ in range(int(delay * 10)):
                if stop_callback and stop_callback():
                    raise ValueError("Download stopped by user")
                time.sleep(0.1)
        except ValueError:
            raise  # Re-raise stop request
        except:
            pass
        
        # Step 2: Make the actual request with full headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Referer': f'{"/".join(page_url.split("/")[:3])}/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
        
        return stealth_session.get(page_url, timeout=30, headers=headers)
    
    def extract_title(self, page_url: str) -> str:
        """
        Extract title from the webpage for filename.
        
        Args:
            page_url: URL of the webpage
            
        Returns:
            Cleaned title string
        """
        try:
            response = self.session.get(page_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to get title from various sources
            title_element = soup.find('title')
            if title_element:
                title = title_element.get_text().strip()
            else:
                # Fallback to URL-based naming
                parsed_url = urlparse(page_url)
                title = parsed_url.path.split('/')[-1] or 'audio'
            
            # Clean the title for use as filename
            title = re.sub(r'[<>:"/\\|?*]', '', title)
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Limit length to avoid filesystem issues
            if len(title) > 100:
                title = title[:100].rsplit(' ', 1)[0]
                
            return title or 'audio'
            
        except Exception:
            # Fallback naming
            return 'audio_download'
    
    def establish_session(self, page_url: str) -> bool:
        """
        Establish a valid session by visiting the webpage first.
        
        Args:
            page_url: URL of the webpage to establish session with
            
        Returns:
            True if session established successfully
        """
        try:
            print("세션 설정 중...")
            
            # Add delay to avoid being flagged as bot
            time.sleep(1)
            
            # First visit with basic headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://japaneseasmr.com/',
            }
            
            response = self.session.get(page_url, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Small delay to mimic human behavior
            time.sleep(2)
            
            print("✓ 세션 설정 완료")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("⚠ 403 오류 - 세션 설정 실패")
                return False
            else:
                print(f"⚠ 경고: 세션 설정 실패: {e}")
                return False
        except Exception as e:
            print(f"⚠ 경고: 세션 설정 실패: {e}")
            return False

    def download_file(self, url: str, filename: str, page_url: str = "") -> bool:
        """
        Download file from URL with progress bar.
        
        Args:
            url: Direct URL to the audio file
            filename: Local filename to save as
            page_url: Original webpage URL for referer header
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            # Check if file already exists
            if os.path.exists(filename):
                print(f"File already exists: {filename}")
                response = input("Overwrite? (y/N): ").strip().lower()
                if response != 'y':
                    return False
            
            print(f"Downloading: {url}")
            
            # Prepare headers for file download
            download_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'audio',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            }
            
            # Add referer if page URL is provided
            if page_url:
                download_headers['Referer'] = page_url
                download_headers['Origin'] = '/'.join(page_url.split('/')[:3])
            
            # Get file size for progress bar
            try:
                head_response = self.session.head(url, headers=download_headers, timeout=30)
                total_size = int(head_response.headers.get('content-length', 0))
            except:
                # If HEAD request fails, proceed without size info
                total_size = 0
            
            # Download with progress bar
            response = self.session.get(url, headers=download_headers, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filename, 'wb') as file, tqdm(
                desc=os.path.basename(filename),
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))
            
            print(f"✓ Successfully downloaded: {filename}")
            return True
            
        except requests.RequestException as e:
            print(f"✗ Download failed: {e}")
            return False
        except Exception as e:
            print(f"✗ Error during download: {e}")
            return False
    
    def download_file_alternative(self, url: str, filename: str, page_url: str = "") -> bool:
        """
        Alternative download method using different techniques.
        
        Args:
            url: Direct URL to the audio file
            filename: Local filename to save as
            page_url: Original webpage URL for referer header
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            import time
            
            print(f"Alternative download: {url}")
            
            # Create a new session with different settings
            alt_session = requests.Session()
            alt_session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Range': 'bytes=0-',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'audio',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            })
            
            if page_url:
                alt_session.headers['Referer'] = page_url
                alt_session.headers['Origin'] = '/'.join(page_url.split('/')[:3])
            
            # First, make a request to the page to establish context
            if page_url:
                try:
                    alt_session.get(page_url, timeout=15)
                    time.sleep(0.5)
                except:
                    pass
            
            # Try downloading with range request
            response = alt_session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filename, 'wb') as file, tqdm(
                desc=f"ALT: {os.path.basename(filename)}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))
            
            print(f"✓ Alternative download successful: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Alternative download failed: {e}")
            return False

    def download_from_url(self, page_url: str, output_dir: str = "downloads", stop_callback=None) -> None:
        """
        Main method to download audio from a webpage URL.
        
        Args:
            page_url: URL of the webpage containing audio
            output_dir: Directory to save downloaded files
            stop_callback: Optional callback function that returns True if download should stop
        """
        try:
            # Create output directory
            Path(output_dir).mkdir(exist_ok=True)
            
            print(f"Analyzing webpage: {page_url}")
            
            # Establish session first
            self.establish_session(page_url)
            
            # Extract audio URLs
            audio_urls = self.extract_audio_urls(page_url, stop_callback)
            print(f"Found {len(audio_urls)} audio source(s)")
            
            # Extract title for filename
            base_title = self.extract_title(page_url)
            
            # Remove duplicates while preserving order
            seen_urls = set()
            unique_audio_urls = []
            for audio_url, format_type in audio_urls:
                if audio_url not in seen_urls:
                    seen_urls.add(audio_url)
                    unique_audio_urls.append((audio_url, format_type))
            
            print(f"Unique audio files to download: {len(unique_audio_urls)}")
            
            # Download each audio file
            for i, (audio_url, format_type) in enumerate(unique_audio_urls):
                if len(unique_audio_urls) > 1:
                    filename = f"{base_title}_{i+1}.{format_type}"
                else:
                    filename = f"{base_title}.{format_type}"
                
                filepath = os.path.join(output_dir, filename)
                
                print(f"\n[{i+1}/{len(unique_audio_urls)}] Format: {format_type.upper()}")
                success = self.download_file(audio_url, filepath, page_url)
                
                if not success:
                    print(f"Skipping {format_type.upper()} download")
                    # Try alternative download method
                    print("Trying alternative download method...")
                    success = self.download_file_alternative(audio_url, filepath, page_url)
                    if success:
                        print(f"✓ Alternative method succeeded for {format_type.upper()}")
                    else:
                        # Final attempt with browser simulation
                        print("Trying final browser simulation method...")
                        success = self.download_file_browser_sim(audio_url, filepath, page_url)
                        if success:
                            print(f"✓ Browser simulation method succeeded for {format_type.upper()}")
                        else:
                            print(f"✗ All download methods failed for {format_type.upper()}")
            
            print(f"\n✓ 오디오 파일 다운로드 완료!")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)


    def download_file_browser_sim(self, url: str, filename: str, page_url: str = "") -> bool:
        """
        Final fallback method that simulates browser behavior very closely.
        
        Args:
            url: Direct URL to the audio file
            filename: Local filename to save as
            page_url: Original webpage URL for referer header
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            print(f"Browser simulation download: {url}")
            
            # Create completely new session
            browser_session = requests.Session()
            
            # Simulate browser startup sequence
            if page_url:
                # Visit main domain first
                domain = '/'.join(page_url.split('/')[:3])
                try:
                    browser_session.get(domain, timeout=10)
                    time.sleep(0.3)
                except:
                    pass
                
                # Visit the actual page
                try:
                    browser_session.get(page_url, timeout=15)
                    time.sleep(0.5)
                except:
                    pass
            
            # Set headers that exactly match a real browser request
            browser_headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'identity;q=1, *;q=0',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Host': urlparse(url).netloc,
                'Pragma': 'no-cache',
                'Range': 'bytes=0-',
                'Sec-Fetch-Dest': 'audio',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            if page_url:
                browser_headers['Referer'] = page_url
                browser_headers['Origin'] = '/'.join(page_url.split('/')[:3])
            
            # Make request with exact browser headers
            response = browser_session.get(
                url, 
                headers=browser_headers,
                stream=True, 
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check if we got the actual file
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                print("⚠ Received HTML instead of audio file - access may be blocked")
                return False
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filename, 'wb') as file, tqdm(
                desc=f"SIM: {os.path.basename(filename)}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=2048):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))
                        time.sleep(0.001)  # Tiny delay to mimic real browser
            
            print(f"✓ Browser simulation download successful: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Browser simulation download failed: {e}")
            return False


def main() -> None:
    """Main function to run the audio downloader."""
    print("🎵 Japanese ASMR Audio Downloader")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter the webpage URL: ").strip()
    
    if not url:
        print("Error: No URL provided")
        sys.exit(1)
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        print("Error: Please provide a valid HTTP/HTTPS URL")
        sys.exit(1)
    
    # Get output directory
    output_dir = input("Enter output directory (default: downloads): ").strip()
    if not output_dir:
        output_dir = "downloads"
    
    # Initialize downloader and start download
    downloader = AudioDownloader()
    downloader.download_from_url(url, output_dir)
    
    print("\n✓ Download process completed!")


if __name__ == "__main__":
    main() 