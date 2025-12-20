from typing import Dict, Type
from .base import BaseParser
from .hwp import HWPParser

class ParserFactory:
    """Factory to provide appropriate parser for file types"""
    
    _parsers: Dict[str, Type[BaseParser]] = {
        '.hwp': HWPParser,
        '.hwpx': HWPParser,
        # Future: .pdf, .docx
    }
    
    @classmethod
    def get_parser(cls, file_path: str) -> BaseParser:
        """
        Get compatible parser instance for the file
        
        Args:
            file_path: Path to the file to parse
        
        Returns:
            Instance of suitable Parser class
            
        Raises:
            ValueError: If no parser is found for the file extension
        """
        ext = '.' + file_path.split('.')[-1].lower() if '.' in file_path else ''
        
        parser_cls = cls._parsers.get(ext)
        if not parser_cls:
            # Fallback or raise? For now raise to be explicit
            raise ValueError(f"No parser available for file type: {ext}")
            
        return parser_cls()
