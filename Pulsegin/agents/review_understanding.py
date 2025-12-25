import re
from typing import Dict, Optional

class ReviewUnderstandingAgent:
    
    def __init__(self):
        self.issue_patterns = [
            r'(?:delivery|deliver|delivered).*?(?:late|delay|slow|delayed)',
            r'(?:food|order|item).*?(?:missing|not.*?delivered|absent)',
            r'(?:food|order).*?(?:wrong|incorrect|different)',
            r'(?:food|item).*?(?:stale|expired|bad.*?quality|poor.*?quality)',
            r'(?:delivery.*?partner|delivery.*?guy|rider|executive).*?(?:rude|impolite|unprofessional)',
            r'(?:customer.*?service|support).*?(?:bad|poor|worst|terrible)',
            r'(?:app|application).*?(?:bug|error|crash|not.*?working)',
            r'(?:payment|refund).*?(?:issue|problem|not.*?working)',
            r'(?:price|cost|charge).*?(?:high|expensive|overpriced)',
            r'(?:order).*?(?:cancel|cancelled|cancellation)',
        ]
        
    def understand_review(self, review_text: str, rating: Optional[int] = None) -> Dict[str, str]:
        if not review_text or not review_text.strip():
            return {
                'summary': 'Empty review',
                'category': 'other'
            }
        
        text = self._clean_text(review_text)
        issues = self._extract_issues(text)
        summary = self._generate_summary(text, issues, rating)
        category = self._categorize(issues, rating)
        
        return {
            'summary': summary,
            'category': category,
            'issues': issues
        }
    
    def _clean_text(self, text: str) -> str:
        text = ' '.join(text.split())
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        return text.lower()
    
    def _extract_issues(self, text: str) -> list:
        issues = []
        for pattern in self.issue_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.extend(matches)
        return list(set(issues))
    
    def _generate_summary(self, text: str, issues: list, rating: Optional[int]) -> str:
        if issues:
            main_issue = issues[0]
            summary = self._normalize_issue(main_issue)
            return summary
        
        words = text.split()
        if len(words) > 20:
            key_phrases = self._extract_key_phrases(text)
            if key_phrases:
                return ' '.join(key_phrases[:3])
        
        sentences = re.split(r'[.!?]+', text)
        if sentences and sentences[0].strip():
            summary = sentences[0].strip()[:100]
        else:
            summary = text[:100]
        
        return summary
    
    def _normalize_issue(self, issue: str) -> str:
        issue_lower = issue.lower()
        
        if 'delivery' in issue_lower and ('late' in issue_lower or 'delay' in issue_lower or 'slow' in issue_lower):
            return 'Delivery delay or late delivery'
        if 'delivery' in issue_lower and ('partner' in issue_lower or 'guy' in issue_lower or 'rider' in issue_lower):
            if 'rude' in issue_lower or 'impolite' in issue_lower:
                return 'Delivery partner rude or unprofessional'
        
        if 'food' in issue_lower or 'item' in issue_lower:
            if 'missing' in issue_lower or 'not delivered' in issue_lower:
                return 'Missing items in order'
            if 'wrong' in issue_lower or 'incorrect' in issue_lower:
                return 'Wrong items delivered'
            if 'stale' in issue_lower or 'expired' in issue_lower:
                return 'Food stale or expired'
            if 'bad' in issue_lower or 'poor' in issue_lower:
                return 'Poor food quality'
        
        if 'customer service' in issue_lower or 'support' in issue_lower:
            return 'Poor customer service'
        
        if 'app' in issue_lower and ('bug' in issue_lower or 'error' in issue_lower or 'crash' in issue_lower):
            return 'App bug or error'
        
        if 'payment' in issue_lower or 'refund' in issue_lower:
            return 'Payment or refund issue'
        
        if 'price' in issue_lower or 'cost' in issue_lower or 'expensive' in issue_lower:
            return 'High prices or overpriced'
        
        if 'cancel' in issue_lower:
            return 'Order cancellation issue'
        
        return issue
    
    def _extract_key_phrases(self, text: str) -> list:
        important_words = ['delivery', 'food', 'order', 'service', 'app', 'payment', 
                          'refund', 'quality', 'missing', 'wrong', 'late', 'rude']
        phrases = []
        words = text.split()
        
        for i, word in enumerate(words):
            if word in important_words:
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                phrase = ' '.join(words[start:end])
                phrases.append(phrase)
        
        return phrases[:5]
    
    def _categorize(self, issues: list, rating: Optional[int]) -> str:
        if rating is not None:
            if rating <= 2:
                return 'complaint'
            elif rating >= 4:
                return 'positive'
            else:
                return 'neutral'
        
        if not issues:
            return 'other'
        
        issue_text = ' '.join(issues).lower()
        if any(word in issue_text for word in ['bad', 'worst', 'poor', 'terrible', 'missing', 'wrong']):
            return 'complaint'
        elif any(word in issue_text for word in ['good', 'great', 'excellent', 'love', 'best']):
            return 'positive'
        else:
            return 'neutral'
