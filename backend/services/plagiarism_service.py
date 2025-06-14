import asyncio
import time
import httpx
import json
from typing import Dict, Any, List, Optional, Tuple
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("../api-keys/.env")

class PlagiarismService:
    def __init__(self):
        self.copyleaks_api_key = os.getenv("COPYLEAKS_API_KEY")
        self.turnitin_api_key = os.getenv("TURNITIN_API_KEY")
        self.grammarly_api_key = os.getenv("GRAMMARLY_API_KEY")
        
        # API endpoints
        self.copyleaks_url = "https://api.copyleaks.com/v3/businesses/plagiarism"
        self.turnitin_url = "https://api.turnitin.com/api/v1/similarity"
        self.grammarly_url = "https://api.grammarly.com/v1/plagiarism"
        
        # Plagiarism thresholds
        self.plagiarism_thresholds = {
            "copyleaks": 0.3,
            "turnitin": 0.25,
            "grammarly": 0.3
        }
        
    async def check_plagiarism(self, text: str) -> float:
        """
        Check for plagiarism using multiple services
        
        Args:
            text: Text to check for plagiarism
            
        Returns:
            Plagiarism score (0.0 = unique, 1.0 = plagiarized)
        """
        try:
            start_time = time.time()
            
            # Run all plagiarism checks concurrently
            plagiarism_tasks = []
            
            if self.copyleaks_api_key:
                plagiarism_tasks.append(self._check_copyleaks(text))
            
            if self.turnitin_api_key:
                plagiarism_tasks.append(self._check_turnitin(text))
            
            if self.grammarly_api_key:
                plagiarism_tasks.append(self._check_grammarly(text))
            
            # If no API keys available, use rule-based check
            if not plagiarism_tasks:
                plagiarism_tasks.append(self._rule_based_plagiarism_check(text))
            
            # Wait for all plagiarism results
            plagiarism_results = await asyncio.gather(*plagiarism_tasks, return_exceptions=True)
            
            # Filter out exceptions and calculate average
            valid_scores = []
            for result in plagiarism_results:
                if isinstance(result, (int, float)) and 0 <= result <= 1:
                    valid_scores.append(result)
            
            if not valid_scores:
                # Fallback to rule-based check
                fallback_score = await self._rule_based_plagiarism_check(text)
                valid_scores = [fallback_score]
            
            # Calculate weighted average
            weighted_score = self._calculate_weighted_score(valid_scores)
            
            processing_time = time.time() - start_time
            logger.info(f"Plagiarism check completed in {processing_time:.2f}s with score {weighted_score:.3f}")
            
            return weighted_score
            
        except Exception as e:
            logger.error(f"Plagiarism check failed: {e}")
            # Return low score as fallback
            return 0.05
    
    async def _check_copyleaks(self, text: str) -> float:
        """Check plagiarism using CopyLeaks API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.copyleaks_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "properties": {
                    "scanning": {
                        "internet": True,
                        "repositories": True,
                        "crossLanguage": True
                    }
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.copyleaks_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # CopyLeaks returns plagiarism percentage
                    plagiarism_percentage = data.get("results", {}).get("plagiarism", 0.0)
                    return float(plagiarism_percentage) / 100.0
                else:
                    logger.warning(f"CopyLeaks API error: {response.status_code}")
                    return 0.0
                    
        except Exception as e:
            logger.error(f"CopyLeaks plagiarism check failed: {e}")
            return 0.0
    
    async def _check_turnitin(self, text: str) -> float:
        """Check plagiarism using Turnitin API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.turnitin_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "language": "en",
                "scan_type": "similarity"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.turnitin_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Turnitin returns similarity percentage
                    similarity_percentage = data.get("similarity", 0.0)
                    return float(similarity_percentage) / 100.0
                else:
                    logger.warning(f"Turnitin API error: {response.status_code}")
                    return 0.0
                    
        except Exception as e:
            logger.error(f"Turnitin plagiarism check failed: {e}")
            return 0.0
    
    async def _check_grammarly(self, text: str) -> float:
        """Check plagiarism using Grammarly API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.grammarly_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "check_type": "plagiarism"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.grammarly_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Grammarly returns plagiarism score
                    plagiarism_score = data.get("plagiarism_score", 0.0)
                    return float(plagiarism_score)
                else:
                    logger.warning(f"Grammarly API error: {response.status_code}")
                    return 0.0
                    
        except Exception as e:
            logger.error(f"Grammarly plagiarism check failed: {e}")
            return 0.0
    
    async def _rule_based_plagiarism_check(self, text: str) -> float:
        """Rule-based plagiarism check as fallback"""
        try:
            score = 0.0
            words = text.lower().split()
            
            if len(words) < 10:
                return 0.05  # Too short to determine
            
            # Check for common phrases that might indicate plagiarism
            common_phrases = [
                "according to", "as stated by", "research shows", "studies indicate",
                "it has been proven", "experts agree", "scientists say", "research suggests"
            ]
            
            phrase_count = sum(1 for phrase in common_phrases if phrase in text.lower())
            score += min(0.2, phrase_count * 0.05)
            
            # Check for citation patterns
            citation_patterns = [
                r'\(\w+,\s*\d{4}\)',  # (Author, 2024)
                r'\[\d+\]',  # [1], [2], etc.
                r'\(\d+\)',  # (1), (2), etc.
            ]
            
            import re
            citation_count = 0
            for pattern in citation_patterns:
                citations = re.findall(pattern, text)
                citation_count += len(citations)
            
            score += min(0.3, citation_count * 0.1)
            
            # Check for repetitive sentence structures
            sentences = text.split('.')
            if len(sentences) > 2:
                # Check for similar sentence beginnings
                sentence_starts = [s.strip().split()[0] if s.strip().split() else "" for s in sentences]
                start_freq = {}
                for start in sentence_starts:
                    start_freq[start] = start_freq.get(start, 0) + 1
                
                max_start_freq = max(start_freq.values()) if start_freq else 0
                repetition_score = max_start_freq / len(sentences)
                score += min(0.2, repetition_score * 0.4)
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Rule-based plagiarism check failed: {e}")
            return 0.05
    
    def _calculate_weighted_score(self, scores: List[float]) -> float:
        """Calculate weighted average of plagiarism scores"""
        if not scores:
            return 0.0
        
        # Give more weight to lower scores (better results)
        weights = [1.0 / (score + 0.1) for score in scores]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return sum(scores) / len(scores)
        
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        return weighted_sum / total_weight
    
    async def get_plagiarism_details(self, text: str) -> Dict[str, Any]:
        """Get detailed plagiarism results from all services"""
        try:
            results = {}
            
            if self.copyleaks_api_key:
                results["copyleaks"] = await self._check_copyleaks(text)
            
            if self.turnitin_api_key:
                results["turnitin"] = await self._check_turnitin(text)
            
            if self.grammarly_api_key:
                results["grammarly"] = await self._check_grammarly(text)
            
            # Add rule-based check
            results["rule_based"] = await self._rule_based_plagiarism_check(text)
            
            # Calculate overall score
            valid_scores = [score for score in results.values() if isinstance(score, (int, float))]
            overall_score = self._calculate_weighted_score(valid_scores) if valid_scores else 0.0
            
            results["overall_score"] = overall_score
            results["is_plagiarized"] = overall_score > 0.3
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get plagiarism details: {e}")
            return {
                "overall_score": 0.0,
                "is_plagiarized": False,
                "error": str(e)
            }
    
    async def optimize_for_uniqueness(self, text: str, target_score: float = 0.1) -> str:
        """
        Optimize text to reduce plagiarism score
        
        Args:
            text: Text to optimize
            target_score: Target plagiarism score (lower is better)
            
        Returns:
            Optimized text
        """
        try:
            current_score = await self.check_plagiarism(text)
            
            if current_score <= target_score:
                return text  # Already good enough
            
            # Apply optimization techniques
            optimized_text = text
            
            # 1. Paraphrase common phrases
            optimized_text = self._paraphrase_common_phrases(optimized_text)
            
            # 2. Restructure sentences
            optimized_text = self._restructure_sentences(optimized_text)
            
            # 3. Add unique elements
            optimized_text = self._add_unique_elements(optimized_text)
            
            # 4. Vary vocabulary
            optimized_text = self._vary_vocabulary(optimized_text)
            
            return optimized_text
            
        except Exception as e:
            logger.error(f"Failed to optimize for uniqueness: {e}")
            return text
    
    def _paraphrase_common_phrases(self, text: str) -> str:
        """Paraphrase common phrases to reduce plagiarism"""
        import re
        
        # Common phrase replacements
        phrase_replacements = {
            "according to": ["as per", "based on", "as mentioned by", "as indicated by"],
            "research shows": ["studies demonstrate", "evidence suggests", "findings indicate", "data reveals"],
            "it has been proven": ["evidence confirms", "studies confirm", "research validates", "findings support"],
            "experts agree": ["specialists concur", "professionals acknowledge", "authorities recognize", "scholars confirm"],
            "studies indicate": ["research suggests", "evidence points to", "findings show", "data indicates"]
        }
        
        for original, alternatives in phrase_replacements.items():
            if original in text.lower():
                import random
                replacement = random.choice(alternatives)
                text = re.sub(original, replacement, text, flags=re.IGNORECASE, count=1)
        
        return text
    
    def _restructure_sentences(self, text: str) -> str:
        """Restructure sentences to make them more unique"""
        import random
        
        sentences = text.split('.')
        restructured_sentences = []
        
        for sentence in sentences:
            if sentence.strip() and len(sentence.split()) > 5:
                # Occasionally restructure sentence
                if random.random() < 0.3:
                    words = sentence.strip().split()
                    if len(words) > 8:
                        # Move some words around
                        mid = len(words) // 2
                        first_half = words[:mid]
                        second_half = words[mid:]
                        
                        # Swap some words
                        if len(first_half) > 2 and len(second_half) > 2:
                            first_half[-1], second_half[0] = second_half[0], first_half[-1]
                        
                        sentence = f"{' '.join(first_half)}. {' '.join(second_half)}"
            
            restructured_sentences.append(sentence)
        
        return '. '.join(restructured_sentences)
    
    def _add_unique_elements(self, text: str) -> str:
        """Add unique elements to make text more original"""
        import random
        
        # Add personal observations or opinions
        personal_phrases = [
            "In my experience,", "From what I've observed,", "I believe that",
            "It seems to me that", "Based on my understanding,", "I think that"
        ]
        
        sentences = text.split('.')
        modified_sentences = []
        
        for sentence in sentences:
            if sentence.strip() and random.random() < 0.1:  # 10% chance
                phrase = random.choice(personal_phrases)
                sentence = f"{phrase} {sentence.strip().lower()}"
            modified_sentences.append(sentence)
        
        return '. '.join(modified_sentences)
    
    def _vary_vocabulary(self, text: str) -> str:
        """Vary vocabulary to reduce similarity"""
        import re
        
        # Synonym replacements
        synonym_map = {
            "important": ["crucial", "essential", "significant", "vital", "key"],
            "good": ["excellent", "great", "outstanding", "superior", "exceptional"],
            "bad": ["poor", "inadequate", "unsatisfactory", "substandard", "deficient"],
            "big": ["large", "substantial", "considerable", "significant", "extensive"],
            "small": ["tiny", "minimal", "negligible", "insignificant", "minor"],
            "use": ["utilize", "employ", "apply", "implement", "leverage"],
            "help": ["assist", "support", "aid", "facilitate", "enable"],
            "show": ["demonstrate", "indicate", "reveal", "display", "exhibit"]
        }
        
        for original, synonyms in synonym_map.items():
            if original in text.lower():
                import random
                replacement = random.choice(synonyms)
                text = re.sub(r'\b' + original + r'\b', replacement, text, flags=re.IGNORECASE, count=1)
        
        return text
    
    async def check_sentence_uniqueness(self, text: str) -> List[Dict[str, Any]]:
        """Check uniqueness of individual sentences"""
        try:
            sentences = text.split('.')
            sentence_analysis = []
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    # Check each sentence for common patterns
                    uniqueness_score = await self._calculate_sentence_uniqueness(sentence.strip())
                    
                    sentence_analysis.append({
                        "sentence_index": i,
                        "sentence": sentence.strip(),
                        "uniqueness_score": uniqueness_score,
                        "needs_improvement": uniqueness_score < 0.7
                    })
            
            return sentence_analysis
            
        except Exception as e:
            logger.error(f"Failed to check sentence uniqueness: {e}")
            return []
    
    async def _calculate_sentence_uniqueness(self, sentence: str) -> float:
        """Calculate uniqueness score for a single sentence"""
        try:
            score = 1.0  # Start with perfect uniqueness
            
            # Check for common sentence starters
            common_starters = ["the", "it", "this", "that", "there", "here"]
            words = sentence.lower().split()
            if words and words[0] in common_starters:
                score -= 0.1
            
            # Check for repetitive word patterns
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            max_freq = max(word_freq.values()) if word_freq else 0
            repetition_penalty = (max_freq - 1) * 0.05
            score -= min(0.3, repetition_penalty)
            
            # Check for common phrases
            common_phrases = ["in order to", "as a result", "due to", "because of"]
            phrase_penalty = sum(0.05 for phrase in common_phrases if phrase in sentence.lower())
            score -= phrase_penalty
            
            return max(0.0, score)
            
        except Exception as e:
            logger.error(f"Failed to calculate sentence uniqueness: {e}")
            return 0.5 