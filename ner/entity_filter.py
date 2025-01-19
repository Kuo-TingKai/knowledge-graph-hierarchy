from typing import List, Dict, Any
import re

class EntityFilter:
    def __init__(self):
        self.categories = {
            'medical_institution': ['診所', '醫院', '集團'],
            'product': ['保養品', '玻尿酸', '精華液'],
            'treatment': ['雷射', '整形', '美容', '醫美'],
            'title': ['醫師', '院長', '主治醫師', '理事長'],
            'specialty': ['皮膚科', '醫學美容', '整形外科']
        }

    def categorize_entity(self, entity: Dict[str, Any]) -> str:
        text = entity['text']
        
        for category, keywords in self.categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'other'

    def filter_medical_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        categorized = {category: [] for category in self.categories.keys()}
        categorized['other'] = []
        
        for entity in entities:
            if entity.get('is_medical', False):
                category = self.categorize_entity(entity)
                if entity['text'] not in categorized[category]:
                    categorized[category].append(entity['text'])
        
        return categorized