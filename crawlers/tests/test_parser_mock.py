import unittest
import sys
import os

# 경로 설정
sys.path.append(os.getcwd())

from kepco.parser import HWPParser

class TestHWPParserLogic(unittest.TestCase):
    """
    HWP 파서 로직 검증 테스트
    (실제 HWP 파일 없이 텍스트 추출 후 정규식 파싱 능력 검증)
    """
    
    def setUp(self):
        self.parser = HWPParser()
        
    def test_parse_korean_specs(self):
        """한글 규격서 텍스트 파싱 테스트"""
        sample_text = """
        [규 격 서]
        1. 품명 : 유연탄 (Bituminous Coal)
        2. 발열량 (Gross Calorific Value) : 5,800 kcal/kg 이상
        3. 유황분 (Sulfur Content) : 1.0 % 이하
        4. 회 분 (Ash) : 14.5 % 미만
        5. 수 분 (Total Moisture) : 12.0% 이하
        6. 휘발분 (Volatile Matter) : 24.0 ~ 35.0 %
        """
        print(f"\n[Test Case 1] Standard Korean Spec\n{sample_text.strip()}")
        
        specs = self.parser.parse_specs(sample_text)
        print(f"-> Parsed: {specs}")
        
        self.assertEqual(specs['gcv'], '5800')
        self.assertEqual(specs['sulfur'], '1.0')
        self.assertEqual(specs['ash'], '14.5')
        self.assertEqual(specs['moisture'], '12.0')
        self.assertEqual(specs['volatile'], '24.0') # 첫 번째 숫자 추출

    def test_parse_english_specs(self):
        """영문 혼용 텍스트 파싱 테스트"""
        sample_text = """
        SPECIFICATION OF COAL
        
        GCV(kcal/kg) : min 6080
        Total Sulfur : max 0.8%
        Ash Content : max 10.0%
        Total Moisture : max 11.5%
        Volatile Matter : 22.0-38.0%
        """
        print(f"\n[Test Case 2] English/Short Spec\n{sample_text.strip()}")
        
        specs = self.parser.parse_specs(sample_text)
        print(f"-> Parsed: {specs}")
        
        self.assertEqual(specs['gcv'], '6080')
        self.assertEqual(specs['sulfur'], '0.8')
        
    def test_messy_format(self):
        """지저분한 포맷 파싱 테스트"""
        sample_text = """
        발열량(kcal/kg):6000이상, 유황분:0.5이하
        회분 :10~12%
        """
        print(f"\n[Test Case 3] Messy Format\n{sample_text.strip()}")
        
        specs = self.parser.parse_specs(sample_text)
        print(f"-> Parsed: {specs}")
        
        self.assertEqual(specs['gcv'], '6000')
        self.assertEqual(specs['sulfur'], '0.5')
        self.assertEqual(specs['ash'], '10')

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
