import olefile
import zlib
import logging
import re
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class HWPParser:
    """
    HWP (Hancom Word Processor) 파일 파서
    - OLE 구조 기반 텍스트 추출
    - 석탄 규격(Spec) 파싱
    """
    
    def __init__(self):
        pass

    def extract_text(self, file_path: str) -> str:
        """HWP 파일에서 텍스트 추출 (PrvText 우선, BodyText 시도)"""
        try:
            if not olefile.isOleFile(file_path):
                logger.warning(f"Not an OLE file: {file_path}")
                return ""

            with olefile.OleFileIO(file_path) as ole:
                # 1. PrvText (미리보기 텍스트) 시도 - 가장 빠름
                if ole.exists("PrvText"):
                    stream = ole.openstream("PrvText")
                    data = stream.read()
                    # HWP 5.0 PrvText is UTF-16LE
                    return data.decode("utf-16-le", errors="ignore")
                
                # 2. BodyText (본문) 시도 - 압축 해제 필요
                # BodyText/Section0, Section1, ...
                text_content = []
                dirs = ole.listdir()
                body_sections = sorted([d[1] for d in dirs if d[0] == "BodyText" and d[1].startswith("Section")])
                
                for section in body_sections:
                    try:
                        stream = ole.openstream(f"BodyText/{section}")
                        data = stream.read()
                        # Inflate (exclude header if needed, but usually zlib handles stream)
                        # HWP BodyText is complicated, raw inflate might fail or produce garbage if not carefully handled.
                        # For simple extraction, we try raw inflate.
                        decompressed = zlib.decompress(data, -15) # -15 for raw inflate
                        # HWP uses UTF-16LE for text
                        text = decompressed.decode("utf-16-le", errors="ignore")
                        text_content.append(text)
                    except Exception as e:
                        logger.debug(f"Failed to decompress section {section}: {e}")
                
                return "\n".join(text_content)

        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""

    def parse_specs(self, text: str) -> Dict[str, str]:
        """텍스트에서 석탄 규격 추출"""
        specs = {}
        
        # 정규식 패턴 (단위 및 공백 유연하게 매칭)
        # 예: 발열량(kcal/kg) : 6,000 이상
        patterns = {
            "gcv":_create_pattern(r"(발열량|GCV|Gross\s*Calorific\s*Value)"),
            "sulfur": _create_pattern(r"(유황분|Sulfur|Total\s*Sulfur)"),
            "ash": _create_pattern(r"(회분|Ash|Ash\s*Content)"),
            "moisture": _create_pattern(r"(수분|Moisture|Total\s*Moisture)"),
            "volatile": _create_pattern(r"(휘발분|Volatile|Volatile\s*Matter)")
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # 숫자 (콤마, 소수점 포함) 추출
                value_str = match.group(2).replace(",", "").strip()
                specs[key] = value_str
                
        return specs

def _create_pattern(keyword_group: str) -> str:
    """값 추출을 위한 정규식 생성 헬퍼"""
    # Keyword ... (some delimiters) ... Value
    return f"{keyword_group}[^0-9]*([0-9,.]+)"

if __name__ == "__main__":
    # Test stub
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 1:
        parser = HWPParser()
        txt = parser.extract_text(sys.argv[1])
        print("--- Extracted Text ---")
        print(txt[:500] + "..." if len(txt) > 500 else txt)
        print("--- Parsed Specs ---")
        print(parser.parse_specs(txt))
