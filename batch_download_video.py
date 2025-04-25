import os
import pandas as pd
from youtube_downloader import download_video
from concurrent.futures import ThreadPoolExecutor, as_completed

def main():
    # 讀取 Excel 檔案
    df = pd.read_excel('google_next_sessions.xlsx')
    url_column = 'YouTube URL'
    output_dir = './downloads/google_next_sessions_video'
    resolution = '720p'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    urls = []
    for idx, row in df.iterrows():
        url = row.get(url_column)
        if isinstance(url, str) and url.strip():
            urls.append((idx+1, url))
        else:
            print(f'第 {idx+1} 筆無有效 YouTube URL，略過')

    # 並行下載
    max_workers = 4  # 可依照你電腦網路/CPU調整
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(download_video, url, output_dir, resolution): (idx, url)
            for idx, url in urls
        }
        for future in as_completed(future_to_url):
            idx, url = future_to_url[future]
            try:
                future.result()
                print(f'第 {idx} 筆下載完成')
            except Exception as e:
                print(f'第 {idx} 筆下載失敗: {url}，錯誤訊息: {e}')

if __name__ == '__main__':
    main()