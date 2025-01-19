from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class KnowledgeBase(ABC):
    @abstractmethod
    def query_hierarchy(self, entity_name: str, relation_type: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_concepts(self, entity_name: str) -> Tuple[List[str], List[str]]:
        pass