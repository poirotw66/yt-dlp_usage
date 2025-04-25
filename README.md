# yt-dlp_usage

本專案提供批次下載 YouTube 影片與音訊的 Python 腳本，適合需要大量下載 YouTube 內容並自動化處理的使用者。

## 目錄結構

- `batch_download_audio.py`：批次下載 YouTube 音訊
- `batch_download_video.py`：批次下載 YouTube 影片
- `youtube_downloader.py`：封裝下載功能的模組
- `google_next_sessions.xlsx`：包含待下載 YouTube 連結的 Excel 檔案

## 需求套件

- Python 3.x
- pandas
- yt-dlp

安裝方式：
```bash
pip install pandas yt-dlp