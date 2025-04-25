#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 影片下載工具

這個腳本使用 yt-dlp 庫來下載 YouTube 影片。
使用方法:
    python youtube_downloader.py <YouTube URL> [輸出路徑]
"""

import os
import sys
import argparse
import re
import urllib.parse
import time
import yt_dlp

def clean_url(url):
    """
    清理 URL，移除轉義字符並確保格式正確
    """
    # 移除轉義字符
    url = url.replace('\\', '')
    
    # 確保 URL 格式正確
    if '&' in url and '?' not in url:
        url = url.replace('&', '?', 1)
    
    # 確保是有效的 URL
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc == '':
        if parsed.path.startswith('youtu.be/') or parsed.path.startswith('youtube.com/'):
            url = 'https://' + parsed.path
    
    # 處理短網址
    if 'youtu.be' in url:
        video_id = url.split('/')[-1]
        url = f'https://www.youtube.com/watch?v={video_id}'
    
    return url

def validate_youtube_url(url):
    """
    驗證 YouTube URL 格式是否正確
    """
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    youtube_match = re.match(youtube_regex, url)
    
    # 如果不匹配，嘗試提取視頻 ID
    if not youtube_match:
        # 嘗試從 URL 中提取視頻 ID
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if video_id_match:
            video_id = video_id_match.group(1)
            print(f"從 URL 中提取到視頻 ID: {video_id}")
            return True
    
    return youtube_match is not None

def download_video(url, output_path=None, resolution='highest'):
    """
    下載 YouTube 影片
    
    參數:
        url (str): YouTube 影片 URL
        output_path (str, optional): 下載影片的保存路徑
        resolution (str, optional): 影片解析度，可以是 'highest', 'lowest' 或特定解析度如 '720p'
    
    返回:
        str: 下載的影片路徑
    """
    try:
        # 清理 URL
        url = clean_url(url)
        print(f"處理後的 URL: {url}")
        
        # 驗證 URL
        if not validate_youtube_url(url):
            print(f"錯誤: '{url}' 不是有效的 YouTube URL")
            return None
        
        # 設置輸出路徑
        if not output_path:
            output_path = os.getcwd()
        
        # 確保輸出路徑存在
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # 設置 yt-dlp 選項
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'verbose': True,
        }
        
        # 根據解析度設置格式
        if resolution == 'highest':
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif resolution == 'lowest':
            ydl_opts['format'] = 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst'
        else:
            # 嘗試匹配特定解析度
            ydl_opts['format'] = f'bestvideo[height<={resolution[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[height<={resolution[:-1]}][ext=mp4]/best'
        
        # 獲取影片信息
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"影片標題: {info.get('title', '未知')}")
            print(f"影片作者: {info.get('uploader', '未知')}")
            print(f"影片長度: {info.get('duration', '未知')} 秒")
        
        # 下載影片
        print(f"開始下載影片，解析度: {resolution}")
        print(f"保存到: {output_path}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # 獲取下載的文件路徑
            if info:
                filename = ydl.prepare_filename(info)
                print(f"下載完成: {filename}")
                return filename
            else:
                print("下載失敗，未能獲取影片信息")
                return None
    
    except Exception as e:
        print(f"下載過程中發生錯誤: {str(e)}")
        print("提示: 請檢查網絡連接，或嘗試更新 yt-dlp 庫 (pip install --upgrade yt-dlp)")
        return None

def download_audio(url, output_path=None):
    """
    只下載 YouTube 影片的音頻部分
    
    參數:
        url (str): YouTube 影片 URL
        output_path (str, optional): 下載音頻的保存路徑
    
    返回:
        str: 下載的音頻路徑
    """
    try:
        # 清理 URL
        url = clean_url(url)
        print(f"處理後的 URL: {url}")
        
        # 驗證 URL
        if not validate_youtube_url(url):
            print(f"錯誤: '{url}' 不是有效的 YouTube URL")
            return None
        
        # 設置輸出路徑
        if not output_path:
            output_path = os.getcwd()
        
        # 確保輸出路徑存在
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # 設置 yt-dlp 選項 - 音頻模式
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'verbose': True,
        }
        
        # 獲取影片信息
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"影片標題: {info.get('title', '未知')}")
            print(f"影片作者: {info.get('uploader', '未知')}")
        
        # 下載音頻
        print(f"開始下載音頻")
        print(f"保存到: {output_path}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # 獲取下載的文件路徑
            if info:
                # 注意：由於後處理器會將文件轉換為 mp3，我們需要修改文件名
                filename = ydl.prepare_filename(info)
                base, _ = os.path.splitext(filename)
                mp3_filename = base + '.mp3'
                print(f"下載完成: {mp3_filename}")
                return mp3_filename
            else:
                print("下載失敗，未能獲取音頻信息")
                return None
    
    except Exception as e:
        print(f"下載過程中發生錯誤: {str(e)}")
        print("提示: 請檢查網絡連接，或嘗試更新 yt-dlp 庫 (pip install --upgrade yt-dlp)")
        return None

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='下載 YouTube 影片')
    parser.add_argument('url', help='YouTube 影片 URL')
    parser.add_argument('-o', '--output', help='輸出路徑', default='./downloads/google_next_sessions')
    parser.add_argument('-r', '--resolution', help='影片解析度 (例如: 720p, 1080p)', default='highest')
    parser.add_argument('-a', '--audio-only', help='只下載音頻', action='store_true')
    
    args = parser.parse_args()
    
    if args.audio_only:
        download_audio(args.url, args.output)
    else:
        download_video(args.url, args.output, args.resolution)

if __name__ == "__main__":
    main()