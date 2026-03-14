import os
import joblib
import re
from typing import Tuple, Dict

class IntentClassifier:
    def __init__(self, model_path='model/intent_clf.joblib'):
        self.model_path = model_path
        self.model = None
        self.load_model()
        
        # Fallback rules for when model is not available
        self.keyword_rules = {
            'faq_fertilizer': ['fertilizer', 'खाद', 'खाद्य', 'उर्वरक', 'manure', 'compost'],
            'faq_loan': ['loan', 'ऋण', 'कर्ज', 'credit', 'borrow', 'money'],
            'market_price': ['price', 'मूल्य', 'कीमत', 'rate', 'market', 'बाजार'],
            'job_search': ['job', 'नौकरी', 'employment', 'work', 'काम', 'रोजगार'],
            'training': ['training', 'प्रशिक्षण', 'skill', 'कौशल', 'learn', 'course'],
            'faq_subsidy': ['subsidy', 'सब्सिडी', 'scheme', 'योजना', 'benefit'],
            'agriculture_help': ['crop', 'फसल', 'disease', 'बीमारी', 'pest', 'farming'],
            'faq_scheme': ['scheme', 'योजना', 'yojana', 'program', 'कार्यक्रम']
        }
    
    def load_model(self):
        """Load the trained model if available"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"[OK] Loaded classifier model from {self.model_path}")
            except Exception as e:
                print(f"[WARN] Could not load model: {e}")
                self.model = None
        else:
            print(f"[WARN] Model not found at {self.model_path}. Using rule-based classification.")
    
    def classify(self, text: str) -> Tuple[str, float, Dict]:
        """
        Classify the intent of the given text
        Returns: (intent, confidence, entities)
        """
        if not text:
            return 'unknown', 0.0, {}
        
        # Clean text
        text_clean = self._clean_text(text)
        
        # Try ML model first
        if self.model is not None:
            try:
                intent = self.model.predict([text_clean])[0]
                # Get probability for confidence
                proba = self.model.predict_proba([text_clean])
                confidence = float(max(proba[0]))
                entities = self._extract_entities(text_clean, intent)
                return intent, confidence, entities
            except Exception as e:
                print(f"[WARN] Model prediction failed: {e}")
        
        # Fallback to rule-based classification
        intent, confidence = self._rule_based_classify(text_clean)
        entities = self._extract_entities(text_clean, intent)
        
        return intent, confidence, entities
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text.lower()
    
    def _rule_based_classify(self, text: str) -> Tuple[str, float]:
        """Fallback rule-based classification using keywords"""
        text_lower = text.lower()
        
        # Check each intent's keywords
        for intent, keywords in self.keyword_rules.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return intent, 0.8
        
        # Default to unknown
        return 'unknown', 0.3
    
    def _extract_entities(self, text: str, intent: str) -> Dict:
        """Extract entities from text based on intent"""
        entities = {}
        
        # Extract phone numbers
        phone_pattern = r'\+?\d[\d\s\-]{8,}\d'
        phones = re.findall(phone_pattern, text)
        if phones:
            entities['phone'] = phones[0]
        
        # Extract numbers (amounts, quantities)
        number_pattern = r'\d+(?:\.\d+)?'
        numbers = re.findall(number_pattern, text)
        if numbers and intent in ['faq_loan', 'market_price']:
            entities['amount'] = numbers[0]
        
        # Extract common crop names
        crop_keywords = ['wheat', 'rice', 'गेहूं', 'धान', 'cotton', 'कपास', 'maize', 'मक्का']
        for crop in crop_keywords:
            if crop in text.lower():
                entities['crop'] = crop
                break
        
        return entities

# Global classifier instance
_classifier = None

def get_classifier():
    """Get or create classifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier