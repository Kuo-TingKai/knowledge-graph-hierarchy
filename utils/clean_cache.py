import json
import os
from pathlib import Path
import argparse

def clean_cache(preview=False):
    # 取得 cache 目錄路徑
    cache_dir = Path('data/cache')
    
    # 確保目錄存在
    if not cache_dir.exists():
        print("Cache directory not found")
        return
    
    # 計數器
    removed = 0
    processed = 0
    
    # 遍歷所有 json 檔案
    for file_path in cache_dir.glob('*.json'):
        processed += 1
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 檢查是否缺少 'value' key
            if 'value' not in data:
                if preview:
                    print(f"Would remove: {file_path.name}")
                else:
                    file_path.unlink()
                    print(f"Removed: {file_path.name}")
                removed += 1
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing {file_path.name}: {str(e)}")
            
    print(f"\nProcessed {processed} files")
    print(f"{'Would remove' if preview else 'Removed'} {removed} files")

def clean_empty_cache():
    """清理空的快取檔案"""
    cache_dir = Path('data/cache')
    if not cache_dir.exists():
        print("快取目錄不存在")
        return
    
    cleaned_count = 0
    for file_path in cache_dir.glob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 檢查是否為空結果
            if (isinstance(data, dict) and 
                'results' in data and 
                'bindings' in data['results'] and 
                len(data['results']['bindings']) == 0):
                
                # 刪除檔案
                file_path.unlink()
                cleaned_count += 1
                print(f"已刪除空快取: {file_path.name}")
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"處理檔案 {file_path.name} 時發生錯誤: {str(e)}")
            continue
    
    print(f"\n清理完成! 共刪除 {cleaned_count} 個空快取檔案")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean cache files')
    parser.add_argument('--preview', action='store_true', help='Preview files to be removed without actually removing them')
    args = parser.parse_args()
    
    clean_cache(preview=args.preview)
    clean_empty_cache()