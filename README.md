# yt-dlp_usage

本專案提供批次下載 YouTube 影片與音訊的 Python 腳本，適合需要大量下載 YouTube 內容並自動化處理的使用者。

## 目錄結構

- `batch_download_audio.py`：批次下載 YouTube 音訊
- `batch_download_video.py`：批次下載 YouTube 影片
- `youtube_downloader.py`：封裝下載功能的模組
- `google_next_sessions.xlsx`：包含待下載 YouTube 連結的 Excel 檔案

## 需求套件

- Python 3.9+（建議）
- pandas
- openpyxl（pandas 讀取 Excel 所需）
- yt-dlp

安裝方式：

```bash
pip install pandas openpyxl yt-dlp
```

## 快速開始

```bash
# 批次下載影片
python batch_download_video.py \
  --input-path google_next_sessions.xlsx \
  --sheet-name Sessions \
  --url-column "YouTube URL" \
  --output-dir ./downloads/video \
  --resolution 720p \
  --max-workers 6 \
  --max-retries 3 \
  --log-file ./logs/video.log

# 批次下載音訊
python batch_download_audio.py \
  --input-path google_next_sessions.xlsx \
  --output-dir ./downloads/audio \
  --max-retries 5 \
  --retry-delay 10
```

若未提供參數，腳本會使用預設值（與舊版一致），因此在 `google_next_sessions.xlsx` + `YouTube URL` 欄位的情況下可以直接執行。

## 常用參數

影片與音訊腳本支援一致的 CLI / JSON 設定。CLI 參數優先權高於設定檔。

| 參數 | 說明 | 預設值 |
| --- | --- | --- |
| `--config` | 指定 JSON 設定檔 | 無 |
| `--input-path` | Excel 檔案路徑 | `google_next_sessions.xlsx` |
| `--sheet-name` | 工作表名稱或索引 | 第一個工作表 |
| `--url-column` | 儲存 YouTube 連結的欄位 | `YouTube URL` |
| `--output-dir` | 下載輸出資料夾 | 音訊：`./downloads/google_next_sessions`<br>影片：`./downloads/google_next_sessions_video` |
| `--limit` | 只處理前 N 筆資料 | 無 |
| `--max-retries` | 單筆失敗後的重試次數 | 3 |
| `--retry-delay` | 每次重試等待的秒數 | 5 |
| `--log-file` | 追加寫入日誌的檔案路徑 | 僅輸出到終端 |
| `--resolution` | （影片）下載解析度 / 模式 | `720p` |
| `--max-workers` | （影片）同時下載線程數 | 4 |

## JSON 設定檔範例

將下列內容儲存為 `config/video.json` 後，可透過 `--config config/video.json` 套用：

```json
{
  "input_path": "google_next_sessions.xlsx",
  "sheet_name": "Sessions",
  "url_column": "YouTube URL",
  "output_dir": "./downloads/google_next_sessions_video",
  "resolution": "1080p",
  "max_workers": 6,
  "max_retries": 5,
  "retry_delay": 8,
  "log_file": "./logs/video.log",
  "limit": 50
}
```

腳本會先載入 JSON 值，再套用 CLI 參數作為覆蓋，因此可以建立不同場景的模板，並在執行時微調個別項目。

## 日誌、進度與重試

- 兩支批次腳本會初始化 `logging`，預設輸出到終端並可選擇寫入檔案。
- 每筆任務都會顯示 `(目前 / 總數)` 的進度摘要，結束時會統計成功／失敗數量。
- 影片與音訊下載皆支援自動重試；若 `youtube_downloader` 回傳失敗或拋出例外，會在等待 `--retry-delay` 秒後再嘗試，直到達到 `--max-retries`。
- `youtube_downloader.py` 也改用標準 logging，單獨執行時會自動設定輸出格式，便於除錯與記錄。

透過上述功能可以將腳本嵌入排程系統或資料管線，發生錯誤時亦能快速回溯問題。完成批次後，可直接檢查產生的日誌或依需要串接通知機制。
