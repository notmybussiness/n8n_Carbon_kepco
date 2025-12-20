from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class CoalSpec:
    """Standardized Coal Specification Data"""
    calorific_value_min: Optional[int] = None
    calorific_value_max: Optional[int] = None
    sulfur_max: Optional[float] = None
    ash_max: Optional[float] = None
    moisture_max: Optional[float] = None
    quantity_mt: Optional[float] = None
    origin: Optional[str] = None
    incoterms: Optional[str] = None

@dataclass
class ParsedDocument:
    """Result of document parsing"""
    file_path: str
    file_type: str
    full_text: str
    coal_spec: Optional[CoalSpec]
    is_coal_related: bool
    keywords_found: List[str]
    metadata: Dict[str, Any] = None

class BaseParser(ABC):
    """Abstract Base Parser Interface"""
    
    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        """Parse a file and return structured data"""
        pass
    
    def validate_extension(self, file_path: str, allowed_extensions: List[str]) -> bool:
        """Helper to validate file extension"""
        return any(file_path.lower().endswith(ext) for ext in allowed_extensions)
