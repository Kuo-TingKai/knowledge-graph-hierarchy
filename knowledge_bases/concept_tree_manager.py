from typing import Dict, List, Any
import json
from pathlib import Path
from .wikidata_client import WikidataClient
import re

class ConceptTreeManager:
    def __init__(self):
        self.wikidata_client = WikidataClient()
        self.trees_dir = Path('data/trees')
        self.trees_dir.mkdir(parents=True, exist_ok=True)
        self.concept_trees = {}

    def build_trees(self, categorized_entities):
        """為所有類別建立概念樹"""
        # 定義類別的根概念和相關詞
        category_configs = {
            'medical_institution': {
                'root': '醫療設施',
                'keywords': ['醫院', '診所', '醫療', '機構']
            },
            'product': {
                'root': '醫療產品',
                'keywords': ['保養品', '藥品', '醫療器材']
            },
            'treatment': {
                'root': '醫療處置',
                'keywords': ['治療', '手術', '美容', '雷射']
            },
            'title': {
                'root': '醫療人員',
                'keywords': ['醫師', '護理師', '醫生']
            },
            'specialty': {
                'root': '醫學專科',
                'keywords': ['科', '專科', '醫學']
            },
            'other': {
                'root': '醫學概念',
                'keywords': ['醫學', '醫療', '健康']
            }
        }
        
        for category, entities in categorized_entities.items():
            if not entities:
                continue
                
            print(f"\n處理 {category} 類別:")
            self.concept_trees[category] = {}
            config = category_configs.get(category, {})
            
            for entity in entities:
                clean_entity = re.sub(r'\([^)]*\)', '', entity).strip()
                print(f"  - 處理 {clean_entity}")
                
                try:
                    # 建立向上的概念樹
                    broader_concepts = self._get_broader_concepts(
                        clean_entity, 
                        config.get('keywords', [])
                    )
                    
                    if broader_concepts:
                        tree = self._build_tree_structure(
                            clean_entity,
                            broader_concepts,
                            config.get('root', '醫學概念')
                        )
                        
                        if tree:
                            self.concept_trees[category][clean_entity] = tree
                            print(f"    ✓ 成功建立概念樹")
                        else:
                            print(f"    ! 無法建立完整樹狀結構")
                    else:
                        print(f"    ! 找不到上位概念")
                        
                except Exception as e:
                    print(f"    x 錯誤: {str(e)}")
                    continue
        
        return self.concept_trees
    
    def _get_broader_concepts(self, entity_name, keywords):
        """獲取實體的上位概念"""
        concepts = []
        results = self.wikidata_client.query_hierarchy(entity_name, 'broader')
        
        if results:
            for result in results:
                label = result.get('itemLabel', {}).get('value')
                if label and any(keyword in label for keyword in keywords):
                    concepts.append(label)
        
        return concepts
    
    def _build_tree_structure(self, entity_name, concepts, root_concept):
        """建立樹狀結構"""
        if not concepts:
            return None
            
        # 確保根概念在最上層
        if root_concept not in concepts:
            concepts.append(root_concept)
            
        # 建立層級結構
        tree = {
            "name": root_concept,
            "level": 0,
            "children": []
        }
        
        current_level = tree
        for level, concept in enumerate(concepts[:-1], 1):
            node = {
                "name": concept,
                "level": level,
                "children": []
            }
            current_level["children"].append(node)
            current_level = node
            
        # 添加原始實體作為葉節點
        current_level["children"].append({
            "name": entity_name,
            "level": len(concepts),
            "children": []
        })
        
        return tree

    def generate_trees(self, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """為每個分類的實體生成概念樹"""
        trees = {}
        
        for category, entity_list in entities.items():
            if category != 'other':
                category_trees = {}
                for entity in entity_list:
                    try:
                        tree = self.wikidata_client.build_concept_tree(entity)
                        if tree.children:  # 只保存有結果的樹
                            category_trees[entity] = self.tree_to_dict(tree)
                    except Exception as e:
                        print(f"處理實體 '{entity}' 時發生錯誤: {str(e)}")
                
                if category_trees:
                    trees[category] = category_trees
        
        return trees

    def tree_to_dict(self, node) -> Dict[str, Any]:
        """將樹節點轉換為字典格式"""
        return {
            'name': node.name,
            'level': node.level,
            'children': [self.tree_to_dict(child) for child in node.children]
        }

    def save_trees(self, trees: Dict[str, Any], filename: str):
        """儲存概念樹到檔案"""
        with open(self.trees_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(trees, f, ensure_ascii=False, indent=2)

    def load_trees(self, filename: str) -> Dict[str, Any]:
        """從檔案載入概念樹"""
        try:
            with open(self.trees_dir / filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}