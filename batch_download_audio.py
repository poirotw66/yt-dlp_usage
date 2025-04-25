import os
import pandas as pd
from youtube_downloader import download_audio

def main():
    # 讀取 Excel 檔案
    df = pd.read_excel('google_next_sessions.xlsx')
    # 假設欄位名稱為 "YouTube URL"
    url_column = 'YouTube URL'
    output_dir = './downloads/google_next_sessions'

    # 若資料夾不存在則建立
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 批次下載
    for idx, row in df.iterrows():
        url = row.get(url_column)
        if isinstance(url, str) and url.strip():
            print(f'正在下載第 {idx+1} 筆: {url}')
            try:
                download_audio(url, output_dir)
            except Exception as e:
                print(f'下載失敗: {url}，錯誤訊息: {e}')
        else:
            print(f'第 {idx+1} 筆無有效 YouTube URL，略過')

if __name__ == '__main__':
    main()