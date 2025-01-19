from SPARQLWrapper import SPARQLWrapper, JSON
from typing import List, Dict, Any, Tuple, Set
import hashlib
import re
from dataclasses import dataclass
from typing import List, Optional

from .base import KnowledgeBase
from config import WIKIDATA_ENDPOINT
from cache.cache_manager import CacheManager

@dataclass
class ConceptNode:
    name: str
    level: int
    children: List['ConceptNode']
    parent: Optional['ConceptNode'] = None

class WikidataClient(KnowledgeBase):
    def __init__(self):
        self.endpoint_url = "https://query.wikidata.org/sparql"
        self.cache_manager = CacheManager()
        
        # 設定 User-Agent 避免被封鎖
        self.endpoint = SPARQLWrapper(WIKIDATA_ENDPOINT)
        self.endpoint.setReturnFormat(JSON)
        self.endpoint.addCustomHttpHeader('User-Agent', 'KnowledgeGraphBot/1.0')
        
        # 定義相關領域的關鍵詞
        self.business_keywords = {
            '商業', '經濟', '市場', '消費', '服務', '產業', '管理', 
            '營銷', '行銷', '銷售', '客戶', '顧客', '價值', '品牌',
            '產品', '療程', '美容', '診所', '門診', '保健', '健康',
            '治療', '醫療', '照護', '護理', '專科', '門診', '臨床',
            '整形', '整型', '美容', '皮膚', '醫美', '外科', '手術',
            '注射', '雷射', '微整', '抗衰', '年輕', '美學'
        }

        # 定義同義詞對應
        self.synonyms = {
            "醫美": ["醫學美容", "醫療美容", "美容醫學", "美容醫療", "整形美容", "美容外科", "整形手術"],
            "整型外科": ["整形外科", "整形", "整型", "美容外科", "整形美容"],
            "皮膚科": ["皮膚醫學", "皮膚醫療", "皮膚美容"],
        }

    def is_chinese(self, text: str) -> bool:
        # 檢查是否包含中文字符
        return bool(re.search('[\u4e00-\u9fff]', text))

    def is_business_related(self, text: str) -> bool:
        """檢查概念是否與商業價值或消費者行為相關"""
        return any(keyword in text for keyword in self.business_keywords)

    def find_related_terms(self, entity_name: str) -> Set[str]:
        """查找相關詞彙"""
        related_terms = {entity_name}
        
        # 檢查同義詞
        for key, values in self.synonyms.items():
            if entity_name in [key] + values:
                related_terms.add(key)
                related_terms.update(values)
        
        return related_terms

    def query_hierarchy(self, entity_name, direction='broader'):
        """查詢實體的上位或下位概念"""
        # 首先嘗試使用實體名稱直接查詢
        query = self._build_hierarchy_query(entity_name, direction)
        results = self._execute_query(query)
        
        # 如果沒有結果，嘗試使用模糊匹配
        if not results:
            query = self._build_fuzzy_query(entity_name, direction)
            results = self._execute_query(query)
            
        return results
    
    def _build_hierarchy_query(self, entity_name, direction='broader'):
        """建立 SPARQL 查詢"""
        # 擴展關係類型
        relations = [
            'wdt:P279',  # subclass of
            'wdt:P31',   # instance of
            'wdt:P361',  # part of
            'wdt:P1269', # facet of
            'wdt:P2283', # uses
            'wdt:P1535', # used by
            'wdt:P452',  # industry
            'wdt:P366',  # has use
            'wdt:P106'   # occupation
        ]
        
        relation_paths = ' | '.join(relations)
        
        if direction == 'broader':
            query = f"""
            SELECT DISTINCT ?item ?itemLabel WHERE {{
              ?entity rdfs:label "{entity_name}"@zh .
              ?entity ({relation_paths})* ?item .
              ?item rdfs:label ?itemLabel .
              FILTER(LANG(?itemLabel) = "zh")
            }}
            """
        else:
            query = f"""
            SELECT DISTINCT ?item ?itemLabel WHERE {{
              ?entity rdfs:label "{entity_name}"@zh .
              ?item ({relation_paths})* ?entity .
              ?item rdfs:label ?itemLabel .
              FILTER(LANG(?itemLabel) = "zh")
            }}
            """
        
        return query
    
    def _build_fuzzy_query(self, entity_name, direction='broader'):
        """使用模糊匹配的查詢"""
        if direction == 'broader':
            query = f"""
            SELECT DISTINCT ?item ?itemLabel WHERE {{
              ?entity rdfs:label ?label .
              FILTER(CONTAINS(?label, "{entity_name}") && LANG(?label) = "zh")
              ?entity wdt:P279* ?item .
              ?item rdfs:label ?itemLabel .
              FILTER(LANG(?itemLabel) = "zh")
            }}
            """
        else:
            query = f"""
            SELECT DISTINCT ?item ?itemLabel WHERE {{
              ?entity rdfs:label ?label .
              FILTER(CONTAINS(?label, "{entity_name}") && LANG(?label) = "zh")
              ?item wdt:P279* ?entity .
              ?item rdfs:label ?itemLabel .
              FILTER(LANG(?itemLabel) = "zh")
            }}
            """
        
        return query

    def _execute_query(self, query):
        self.endpoint.setQuery(query)
        try:
            results = self.endpoint.query().convert()
            return results
        except Exception as e:
            print(f"查詢執行錯誤: {str(e)}")
            return {"results": {"bindings": []}}

    def get_concepts(self, entity_name: str) -> Tuple[List[str], List[str]]:
        """返回上位概念和下位概念的元組"""
        broader_results = self.query_hierarchy(entity_name, 'broader')
        narrower_results = self.query_hierarchy(entity_name, 'narrower')
        
        broader_concepts = []
        narrower_concepts = []
        
        # 處理上位概念
        for result in broader_results['results']['bindings']:
            if 'itemLabel' in result:
                label = result['itemLabel']['value']
                if self.is_chinese(label) and self.is_business_related(label):
                    broader_concepts.append(label)
        
        # 反轉上位概念順序，使最一般的概念在最上層
        broader_concepts = list(reversed(sorted(set(broader_concepts))))
        
        # 處理下位概念
        for result in narrower_results['results']['bindings']:
            if 'itemLabel' in result:
                label = result['itemLabel']['value']
                if self.is_chinese(label) and self.is_business_related(label):
                    narrower_concepts.append(label)
        
        return (broader_concepts, sorted(list(set(narrower_concepts))))

    def build_concept_tree(self, entity_name: str) -> ConceptNode:
        """建立概念樹"""
        broader_concepts, narrower_concepts = self.get_concepts(entity_name)
        
        # 建立層級關係
        if broader_concepts:
            # 從最上層開始建立樹
            root = ConceptNode(name=broader_concepts[0], level=0, children=[])
            current = root
            
            # 建立中間層級
            for concept in broader_concepts[1:]:
                node = ConceptNode(name=concept, level=current.level + 1, children=[])
                node.parent = current
                current.children = [node]
                current = node
            
            # 添加當前實體
            entity_node = ConceptNode(name=entity_name, level=current.level + 1, children=[])
            entity_node.parent = current
            current.children = [entity_node]
            
            # 添加下位概念
            for concept in sorted(narrower_concepts):
                node = ConceptNode(name=concept, level=entity_node.level + 1, children=[])
                node.parent = entity_node
                entity_node.children.append(node)
        else:
            # 如果沒有上位概念，直接從當前實體開始
            root = ConceptNode(name=entity_name, level=0, children=[])
            for concept in sorted(narrower_concepts):
                node = ConceptNode(name=concept, level=1, children=[])
                node.parent = root
                root.children.append(node)
        
        return root

    def print_tree(self, node: ConceptNode, indent: str = "", is_last: bool = True) -> str:
        """格式化輸出概念樹"""
        result = []
        
        if node.level >= 0:
            marker = "└───" if is_last else "├───"
            prefix = indent + marker
            result.append(f"{prefix} {node.name}")
            indent += "    " if is_last else "│   "
        
        # 處理子節點
        children = sorted(node.children, key=lambda x: x.name)
        for i, child in enumerate(children):
            is_last_child = i == len(children) - 1
            result.append(self.print_tree(child, indent, is_last_child))
        
        return "\n".join(filter(None, result))