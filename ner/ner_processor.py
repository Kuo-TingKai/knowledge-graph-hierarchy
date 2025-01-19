import spacy
from typing import List, Dict, Any
import json
from pathlib import Path

class NERProcessor:
    def __init__(self):
        self.nlp = spacy.load("zh_core_web_sm")
        self.medical_keywords = {
            '醫學', '醫療', '美容', '皮膚', '診所', '醫師', '醫院',
            '保養品', '玻尿酸', '雷射', '整形', '醫美'
        }

    def process_text(self, text: str) -> List[Dict[str, Any]]:
        doc = self.nlp(text)
        entities = []
        
        # 增加基於規則的實體識別
        for token in doc:
            # 檢查是否包含醫療相關關鍵詞
            for keyword in self.medical_keywords:
                if keyword in token.text:
                    entity_info = {
                        'text': token.text,
                        'label': 'MEDICAL',
                        'start': token.idx,
                        'end': token.idx + len(token.text),
                        'is_medical': True
                    }
                    entities.append(entity_info)
                    break
        
        # 合併 spaCy 的 NER 結果
        for ent in doc.ents:
            entity_info = {
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'is_medical': any(keyword in ent.text for keyword in self.medical_keywords)
            }
            entities.append(entity_info)
        
        # 去重
        unique_entities = []
        seen = set()
        for entity in entities:
            if entity['text'] not in seen:
                seen.add(entity['text'])
                unique_entities.append(entity)
        
        return unique_entities

    def save_results(self, entities: List[Dict[str, Any]], filename: str):
        output_dir = Path('data/ner')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(entities, f, ensure_ascii=False, indent=2)
