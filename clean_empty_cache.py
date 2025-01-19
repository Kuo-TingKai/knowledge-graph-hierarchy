import json
import os
from pathlib import Path

def clean_empty_cache():
    # 設定快取目錄路徑
    cache_dir = Path('data/cache')
    
    # 確保目錄存在
    if not cache_dir.exists():
        print(f"快取目錄不存在: {cache_dir}")
        return
    
    # 計數器
    total_files = 0
    deleted_files = 0
    
    # 遍歷所有 json 檔案
    for file_path in cache_dir.glob('*.json'):
        total_files += 1
        try:
            # 讀取 JSON 檔案
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 檢查是否為空結果
            if (isinstance(data, dict) and 
                'results' in data and 
                'bindings' in data['results'] and 
                len(data['results']['bindings']) == 0):
                
                # 刪除檔案
                file_path.unlink()
                deleted_files += 1
                print(f"已刪除空快取檔案: {file_path.name}")
                
        except json.JSONDecodeError:
            print(f"無法解析 JSON 檔案: {file_path.name}")
        except Exception as e:
            print(f"處理檔案時發生錯誤 {file_path.name}: {str(e)}")
    
    # 輸出統計資訊
    print(f"\n清理完成!")
    print(f"總檔案數: {total_files}")
    print(f"已刪除空快取檔案數: {deleted_files}")

if __name__ == "__main__":
    clean_empty_cache()