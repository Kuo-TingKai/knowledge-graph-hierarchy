from SPARQLWrapper import SPARQLWrapper, JSON
from typing import List, Dict, Any
import hashlib

from .base import KnowledgeBase
from config import DBPEDIA_ENDPOINT
from cache.cache_manager import CacheManager

class DBpediaClient(KnowledgeBase):
    def __init__(self):
        self.endpoint = SPARQLWrapper(DBPEDIA_ENDPOINT)
        self.endpoint.setReturnFormat(JSON)
        self.cache = CacheManager()
        # 設定 User-Agent 避免被封鎖
        self.endpoint.addCustomHttpHeader('User-Agent', 'KnowledgeGraphBot/1.0 (kevin@example.com)')

    def query_concept_hierarchy(self, entity_name: str) -> Dict[str, Any]:
        cache_key = f"dbpedia_{hashlib.md5(entity_name.encode()).hexdigest()}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT DISTINCT ?broader ?broaderLabel
        WHERE {
          ?concept rdfs:label ?label .
          ?concept dct:subject|dbo:type|rdf:type ?broader .
          ?broader rdfs:label ?broaderLabel .
          FILTER(LANG(?label) IN ("zh", "zh-tw", "zh-hant") && str(?label) = "%s")
          FILTER(LANG(?broaderLabel) IN ("zh", "zh-tw", "zh-hant"))
        }
        LIMIT 10
        """ % entity_name

        self.endpoint.setQuery(query)
        results = self.endpoint.query().convert()
        
        self.cache.set(cache_key, results)
        return results

    def get_broader_concepts(self, entity_name: str) -> List[str]:
        try:
            results = self.query_concept_hierarchy(entity_name)
            return [x['broaderLabel']['value'] 
                    for x in results['results']['bindings']]
        except Exception as e:
            print(f"查詢錯誤詳情: {str(e)}")
            return []