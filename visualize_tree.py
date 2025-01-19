import json
from graphviz import Digraph
from pathlib import Path
import re

def clean_name(name):
    """清理名稱，移除特殊字符"""
    return re.sub(r'[^\w\s-]', '', name)

def create_tree_visualization(output_path='visualization'):
    """創建概念樹的視覺化圖形"""
    
    # 讀取 JSON 數據
    try:
        with open('data/trees/concept_trees.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("錯誤: 找不到 data/trees/concept_trees.json 檔案")
        return
    except json.JSONDecodeError:
        print("錯誤: JSON 檔案格式不正確")
        return
    
    # 確保輸出目錄存在
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    def add_nodes(dot, node, parent_id=None, prefix=''):
        """遞迴添加節點到圖形"""
        # 為每個節點創建唯一ID
        current_id = f"{prefix}_{clean_name(node['name'])}"
        
        # 根據層級設定節點顏色
        colors = {
            0: '#E8F8F5',  # 最淺的藍綠色
            1: '#D1F2EB',
            2: '#A3E4D7',
            3: '#76D7C4',
            4: '#48C9B0'   # 最深的藍綠色
        }
        
        # 獲取節點顏色
        fillcolor = colors.get(node.get('level', 0), '#E8F8F5')
        
        # 添加節點
        dot.node(current_id, 
                node['name'], 
                fillcolor=fillcolor,
                style='filled,rounded')
        
        # 如果有父節點，添加邊
        if parent_id:
            dot.edge(parent_id, current_id)
        
        # 遞迴處理子節點
        for i, child in enumerate(node.get('children', [])):
            add_nodes(dot, child, current_id, f"{prefix}_{i}")
    
    # 為每個主要類別創建單獨的圖
    for category, category_data in data.items():
        print(f"\n處理類別: {category}")
        
        for concept, tree in category_data.items():
            print(f"  生成概念樹: {concept}")
            
            # 創建新的圖形
            dot = Digraph(comment=f'{category} - {concept}')
            dot.attr(rankdir='TB')  # 從上到下的布局
            
            # 設定圖形屬性
            dot.attr('node', 
                    shape='box',
                    style='rounded',
                    fontname='Microsoft JhengHei')  # 使用正黑體
            
            # 添加所有節點
            add_nodes(dot, tree)
            
            # 保存圖形
            output_file = f"{output_path}/{category}_{clean_name(concept)}"
            try:
                dot.render(output_file, format='png', cleanup=True)
                print(f"    已生成圖形: {output_file}.png")
            except Exception as e:
                print(f"    生成圖形時發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("開始生成概念樹視覺化...")
    create_tree_visualization()
    print("\n完成!")