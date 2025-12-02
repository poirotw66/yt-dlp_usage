import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import pandas as pd

from youtube_downloader import download_audio


DEFAULT_SETTINGS: Dict[str, Any] = {
    'input_path': 'google_next_sessions.xlsx',
    'sheet_name': None,
    'url_column': 'YouTube URL',
    'output_dir': './downloads/google_next_sessions',
    'max_retries': 3,
    'retry_delay': 5,
    'log_file': None,
    'limit': None,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='批次下載 Excel 清單中的 YouTube 音訊'
    )
    parser.add_argument('--config', help='JSON 設定檔路徑')
    parser.add_argument('-i', '--input-path', help='Excel 檔案路徑')
    parser.add_argument('-s', '--sheet-name', help='Excel 表單名稱或索引')
    parser.add_argument('-c', '--url-column', help='儲存 YouTube URL 的欄位名稱')
    parser.add_argument('-o', '--output-dir', help='輸出資料夾')
    parser.add_argument('-l', '--limit', type=int, help='僅處理前 N 筆記錄')
    parser.add_argument('--max-retries', type=int, help='單筆失敗時的重試次數')
    parser.add_argument('--retry-delay', type=int, help='重試前等待秒數')
    parser.add_argument('--log-file', help='將日誌寫入指定檔案')
    return parser.parse_args()


def load_config(config_path: Optional[str]) -> Dict[str, Any]:
    if not config_path:
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
            if not isinstance(data, dict):
                raise ValueError('設定檔必須是 JSON 物件')
            return data
    except FileNotFoundError as exc:
        raise SystemExit(f'找不到設定檔: {config_path}') from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f'設定檔解析失敗: {config_path}') from exc


def resolve_settings(args: argparse.Namespace) -> Dict[str, Any]:
    settings = DEFAULT_SETTINGS.copy()
    settings.update(load_config(getattr(args, 'config', None)))

    for key, value in vars(args).items():
        if key == 'config' or value is None:
            continue
        settings[key] = value

    normalized_settings = {
        key.replace('-', '_'): value for key, value in settings.items()
    }
    normalized_settings['output_dir'] = str(normalized_settings['output_dir'])
    normalized_settings['input_path'] = str(normalized_settings['input_path'])
    log_path = normalized_settings.get('log_file')
    if log_path is not None:
        normalized_settings['log_file'] = str(log_path)

    limit_value = normalized_settings.get('limit')
    if limit_value is not None:
        normalized_settings['limit'] = int(limit_value)

    sheet_value = normalized_settings.get('sheet_name')
    if isinstance(sheet_value, str) and sheet_value.isdigit():
        normalized_settings['sheet_name'] = int(sheet_value)

    normalized_settings['max_retries'] = int(normalized_settings['max_retries'])
    normalized_settings['retry_delay'] = int(normalized_settings['retry_delay'])

    return normalized_settings


def read_urls_from_excel(
    input_path: str,
    sheet_name: Optional[str],
    url_column: str,
    limit: Optional[int],
) -> List[Tuple[int, str]]:
    try:
        df = pd.read_excel(
            input_path,
            sheet_name=sheet_name if sheet_name not in (None, '') else 0,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f'找不到 Excel 檔案: {input_path}') from exc

    if url_column not in df.columns:
        available = ', '.join(df.columns)
        raise SystemExit(
            f'欄位 "{url_column}" 不存在，請確認 Excel。可用欄位: {available}'
        )

    urls: List[Tuple[int, str]] = []
    for idx, url in enumerate(df[url_column], start=1):
        if isinstance(url, str) and url.strip():
            urls.append((idx, url.strip()))
        else:
            print(f'第 {idx} 筆無有效 YouTube URL，略過')

    if limit is not None:
        urls = urls[:limit]

    return urls


def setup_logging(log_file: Optional[str]) -> None:
    handlers = [logging.StreamHandler()]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding='utf-8'))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=handlers,
        force=True,
    )


def download_with_retry(
    url: str,
    output_dir: str,
    max_retries: int,
    retry_delay: int,
) -> Optional[str]:
    last_error: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            result = download_audio(url, output_dir)
            if result:
                return result
            raise RuntimeError('下載函式未回傳檔案路徑')
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < max_retries:
                logging.warning(
                    '下載失敗，將於 %d 秒後重試 (%d/%d): %s',
                    retry_delay,
                    attempt,
                    max_retries,
                    url,
                )
                time.sleep(retry_delay)
            else:
                break
    if last_error:
        raise last_error
    raise RuntimeError('下載失敗且無可用錯誤訊息')


def main() -> None:
    args = parse_args()
    settings = resolve_settings(args)

    setup_logging(settings.get('log_file'))

    Path(settings['output_dir']).mkdir(parents=True, exist_ok=True)

    urls = read_urls_from_excel(
        settings['input_path'],
        settings.get('sheet_name'),
        settings['url_column'],
        settings.get('limit'),
    )

    if not urls:
        logging.info('沒有有效的下載目標，結束。')
        return

    logging.info('批次下載設定:')
    for key in ('input_path', 'sheet_name', 'url_column', 'output_dir', 'limit', 'max_retries', 'retry_delay', 'log_file'):
        logging.info('  %s: %s', key, settings.get(key))

    total = len(urls)
    completed = 0
    failed = 0

    for idx, url in urls:
        logging.info('(%d/%d) 正在下載第 %d 筆: %s', completed + failed + 1, total, idx, url)
        try:
            result = download_with_retry(
                url,
                settings['output_dir'],
                settings['max_retries'],
                settings['retry_delay'],
            )
            completed += 1
            logging.info('第 %d 筆完成: %s', idx, result or '無檔名')
        except Exception as exc:
            failed += 1
            logging.error('第 %d 筆失敗: %s，錯誤訊息: %s', idx, url, exc)

    logging.info('批次完成，成功 %d 筆，失敗 %d 筆', completed, failed)


if __name__ == '__main__':
    main()