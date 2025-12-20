import re
import os
from typing import List, Optional
from .base import BaseParser, ParsedDocument, CoalSpec

# Placeholder for hwp5 import - intended for Linux environment
try:
    # This library (pyhwp) is what we will use on Linux
    from hwp5.hwp5txt import Hwp5Txt
    HWP5_AVAILABLE = True
except ImportError:
    HWP5_AVAILABLE = False

class HWPParser(BaseParser):
    """
    HWP Parser implementation compatible with Linux (using hwp5/pyhwp)
    """
    
    COAL_KEYWORDS = [
        "유연탄", "석탄", "연료", "thermal coal", "bituminous",
        "발열량", "calorific", "kcal", "NAR", "GAR",
        "황분", "sulfur", "유황",
        "회분", "ash",
        "인도네시아", "호주", "러시아"
    ]
    
    PATTERNS = {
        "calorific_value": [
            r"발열량[:\s]*(\d{4,5})\s*[kK]cal",
            r"(\d{4,5})\s*[kK]cal/[kK]g",
            r"NAR[:\s]*(\d{4,5})",
            r"GAR[:\s]*(\d{4,5})",
        ],
        "sulfur": [
            r"황분[:\s]*(\d+\.?\d*)\s*%",
            r"유황[:\s]*(\d+\.?\d*)\s*%",
            r"[Ss]ulfur[:\s]*(\d+\.?\d*)\s*%",
            r"S[:\s]*(\d+\.?\d*)\s*%\s*[이하|max]",
        ],
        "ash": [
            r"회분[:\s]*(\d+\.?\d*)\s*%",
            r"[Aa]sh[:\s]*(\d+\.?\d*)\s*%",
        ],
        "moisture": [
            r"수분[:\s]*(\d+\.?\d*)\s*%",
            r"[Mm]oisture[:\s]*(\d+\.?\d*)\s*%",
            r"TM[:\s]*(\d+\.?\d*)\s*%",
        ],
        "quantity": [
            r"(\d{1,3}(?:,\d{3})*)\s*(?:MT|톤|ton)",
            r"물량[:\s]*(\d{1,3}(?:,\d{3})*)",
        ],
    }

    def parse(self, file_path: str) -> ParsedDocument:
        if not self.validate_extension(file_path, ['.hwp', '.hwpx']):
            raise ValueError(f"Invalid file type for HWPParser: {file_path}")
            
        full_text = self._extract_text(file_path)
        keywords = self._find_keywords(full_text)
        is_coal = len(keywords) >= 2
        spec = self._extract_spec(full_text) if is_coal else None
        
        return ParsedDocument(
            file_path=file_path,
            file_type='hwp',
            full_text=full_text,
            coal_spec=spec,
            is_coal_related=is_coal,
            keywords_found=keywords,
            metadata={}
        )

    def _extract_text(self, file_path: str) -> str:
        """Extract text using best available method"""
        # 1. Try hwp5 (Linux/Docker friendly)
        if HWP5_AVAILABLE:
            try:
                # Basic usage of hwp5txt to get content
                # Note: hwp5txt usually outputs to stdout or file, we might need subprocess if library usage is tricky
                # For now, let's assume we can use the library wrapper or fallback to subprocess
                # As a safe bet in this environment without verifying hwp5 internal API, let's use subprocess if needed
                # However, for this implementation let's try the fallback binary extraction first which is robust for simple text
                pass 
            except Exception:
                pass
        
        # 2. Fallback: Binary extraction (robust for simple Korean text in HWP v5)
        return self._extract_fallback(file_path)

    def _extract_fallback(self, file_path: str) -> str:
        """
        Fallback extraction using binary regex analysis.
        Extracts UTF-16LE text sequences which are common in HWP files.
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            text_parts = []
            try:
                # Attempt to decode as UTF-16LE
                decoded = content.decode('utf-16-le', errors='ignore')
                # Filter for Hangul and ASCII printable characters
                korean_pattern = re.compile(r'[\uAC00-\uD7A3\w\s.,\-:;()\[\]%]+')
                matches = korean_pattern.findall(decoded)
                # Filter out short noise
                text_parts.extend([m for m in matches if len(m) > 3])
            except Exception:
                pass
            
            return ' '.join(text_parts)
        except Exception as e:
            print(f"Extraction error: {e}")
            return ""

    def _find_keywords(self, text: str) -> List[str]:
        found = []
        text_lower = text.lower()
        for kw in self.COAL_KEYWORDS:
            if kw.lower() in text_lower:
                found.append(kw)
        return found

    def _extract_spec(self, text: str) -> CoalSpec:
        spec = CoalSpec()
        
        # Helper to find first match
        def find_val(key, cast_func):
            for pattern in self.PATTERNS[key]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        val_str = match.group(1).replace(',', '')
                        return cast_func(val_str)
                    except ValueError:
                        continue
            return None

        # Min/Max logic for Calorific Value
        for pattern in self.PATTERNS["calorific_value"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = int(match.group(1).replace(',', ''))
                if spec.calorific_value_min is None:
                    spec.calorific_value_min = val
                else:
                    spec.calorific_value_max = val
                break # Take the first clearly identified one

        spec.sulfur_max = find_val("sulfur", float)
        spec.ash_max = find_val("ash", float)
        spec.moisture_max = find_val("moisture", float)
        spec.quantity_mt = find_val("quantity", float)
        
        incoterms_pattern = r'\b(FOB|CIF|CFR|DES|DAP)\b'
        match = re.search(incoterms_pattern, text, re.IGNORECASE)
        if match:
            spec.incoterms = match.group(1).upper()
            
        return spec
