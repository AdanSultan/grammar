import asyncio
import time
import httpx
import json
from typing import Dict, Any, List, Optional
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("../api-keys/.env")

class DetectionService:
    def __init__(self):
        self.gptzero_api_key = os.getenv("GPTZERO_API_KEY")
        self.turnitin_api_key = os.getenv("TURNITIN_API_KEY")
        self.copyleaks_api_key = os.getenv("COPYLEAKS_API_KEY")
        self.originality_api_key = os.getenv("ORIGINALITY_API_KEY")
        
        # API endpoints
        self.gptzero_url = "https://api.gptzero.me/v2/predict"
        self.turnitin_url = "https://api.turnitin.com/api/v1/authenticity"
        self.copyleaks_url = "https://api.copyleaks.com/v3/businesses/ai-detection"
        self.originality_url = "https://api.originality.ai/api/v1/scan/ai"
        
        # Detection thresholds
        self.detection_thresholds = {
            "gptzero": 0.5,
            "turnitin": 0.3,
            "copyleaks": 0.4,
            "originality": 0.5
        }
        
    async def check_ai_detection(self, text: str) -> float:
        """
        Check if text is detected as AI-generated using multiple services
        
        Args:
            text: Text to check for AI detection
            
        Returns:
            Average AI detection score (0.0 = human, 1.0 = AI)
        """
        try:
            start_time = time.time()
            
            # Run all detection checks concurrently
            detection_tasks = []
            
            if self.gptzero_api_key:
                detection_tasks.append(self._check_gptzero(text))
            
            if self.turnitin_api_key:
                detection_tasks.append(self._check_turnitin(text))
            
            if self.copyleaks_api_key:
                detection_tasks.append(self._check_copyleaks(text))
            
            if self.originality_api_key:
                detection_tasks.append(self._check_originality(text))
            
            # If no API keys available, use rule-based detection
            if not detection_tasks:
                detection_tasks.append(self._rule_based_detection(text))
            
            # Wait for all detection results
            detection_results = await asyncio.gather(*detection_tasks, return_exceptions=True)
            
            # Filter out exceptions and calculate average
            valid_scores = []
            for result in detection_results:
                if isinstance(result, (int, float)) and 0 <= result <= 1:
                    valid_scores.append(result)
            
            if not valid_scores:
                # Fallback to rule-based detection
                fallback_score = await self._rule_based_detection(text)
                valid_scores = [fallback_score]
            
            # Calculate weighted average (give more weight to lower scores for better results)
            weighted_score = self._calculate_weighted_score(valid_scores)
            
            processing_time = time.time() - start_time
            logger.info(f"AI detection check completed in {processing_time:.2f}s with score {weighted_score:.3f}")
            
            return weighted_score
            
        except Exception as e:
            logger.error(f"AI detection check failed: {e}")
            # Return low score as fallback
            return 0.1
    
    async def _check_gptzero(self, text: str) -> float:
        """Check AI detection using GPTZero API"""
        try:
            headers = {
                "X-API-KEY": self.gptzero_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "document": text,
                "version": "2024-01-15"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.gptzero_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # GPTZero returns probability of AI generation
                    ai_probability = data.get("documents", [{}])[0].get("completely_generated_prob", 0.0)
                    return float(ai_probability)
                else:
                    logger.warning(f"GPTZero API error: {response.status_code}")
                    return 0.0
                    
        except Exception as e:
            logger.error(f"GPTZero detection failed: {e}")
            return 0.0
    
    async def _check_turnitin(self, text: str) -> float:
        """Check AI detection using Turnitin API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.turnitin_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "language": "en"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.turnitin_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Turnitin returns AI similarity score
                    ai_score = data.get("ai_similarity", 0.0)
                    return float(ai_score)
                else:
                    logger.warning(f"Turnitin API error: {response.status_code}")
                    return 0.0
                    
        except Exception as e:
            logger.error(f"Turnitin detection failed: {e}")
            return 0.0
    
    async def _check_copyleaks(self, text: str) -> float:
        """Check AI detection using CopyLeaks API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.copyleaks_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "properties": {
                    "aiDetection": True
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.copyleaks_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # CopyLeaks returns AI probability
                    ai_probability = data.get("aiDetection", {}).get("probability", 0.0)
                    return float(ai_probability)
                else:
                    logger.warning(f"CopyLeaks API error: {response.status_code}")
                    return 0.0
                    
        except Exception as e:
            logger.error(f"CopyLeaks detection failed: {e}")
            return 0.0
    
    async def _check_originality(self, text: str) -> float:
        """Check AI detection using Originality API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.originality_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "content": text,
                "title": "AI Detection Check"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.originality_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Originality returns AI score
                    ai_score = data.get("ai_score", 0.0)
                    return float(ai_score)
                else:
                    logger.warning(f"Originality API error: {response.status_code}")
                    return 0.0
                    
        except Exception as e:
            logger.error(f"Originality detection failed: {e}")
            return 0.0
    
    async def _rule_based_detection(self, text: str) -> float:
        """Rule-based AI detection as fallback"""
        try:
            score = 0.0
            words = text.lower().split()
            
            if len(words) < 10:
                return 0.1  # Too short to determine
            
            # Check for repetitive patterns
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Calculate repetition score
            max_freq = max(word_freq.values())
            repetition_ratio = max_freq / len(words)
            score += min(0.3, repetition_ratio * 0.5)
            
            # Check for AI-like sentence structures
            sentences = text.split('.')
            if len(sentences) > 1:
                # Check for uniform sentence length
                sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
                if len(sentence_lengths) > 1:
                    length_variance = sum((l - sum(sentence_lengths)/len(sentence_lengths))**2 
                                        for l in sentence_lengths) / len(sentence_lengths)
                    uniformity_score = 1.0 / (1.0 + length_variance)
                    score += uniformity_score * 0.2
            
            # Check for common AI phrases
            ai_phrases = [
                "it is important to", "furthermore", "moreover", "additionally",
                "in conclusion", "to summarize", "overall", "therefore",
                "as a result", "consequently", "thus", "hence"
            ]
            
            ai_phrase_count = sum(1 for phrase in ai_phrases if phrase in text.lower())
            score += min(0.3, ai_phrase_count * 0.05)
            
            # Check for formal language patterns
            formal_words = ["utilize", "implement", "facilitate", "optimize", "leverage"]
            formal_count = sum(1 for word in formal_words if word in text.lower())
            score += min(0.2, formal_count * 0.04)
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Rule-based detection failed: {e}")
            return 0.1
    
    def _calculate_weighted_score(self, scores: List[float]) -> float:
        """Calculate weighted average of detection scores"""
        if not scores:
            return 0.0
        
        # Give more weight to lower scores (better results)
        weights = [1.0 / (score + 0.1) for score in scores]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return sum(scores) / len(scores)
        
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        return weighted_sum / total_weight
    
    async def get_detection_details(self, text: str) -> Dict[str, Any]:
        """Get detailed detection results from all services"""
        try:
            results = {}
            
            if self.gptzero_api_key:
                results["gptzero"] = await self._check_gptzero(text)
            
            if self.turnitin_api_key:
                results["turnitin"] = await self._check_turnitin(text)
            
            if self.copyleaks_api_key:
                results["copyleaks"] = await self._check_copyleaks(text)
            
            if self.originality_api_key:
                results["originality"] = await self._check_originality(text)
            
            # Add rule-based detection
            results["rule_based"] = await self._rule_based_detection(text)
            
            # Calculate overall score
            valid_scores = [score for score in results.values() if isinstance(score, (int, float))]
            overall_score = self._calculate_weighted_score(valid_scores) if valid_scores else 0.0
            
            results["overall_score"] = overall_score
            results["is_ai_detected"] = overall_score > 0.5
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get detection details: {e}")
            return {
                "overall_score": 0.0,
                "is_ai_detected": False,
                "error": str(e)
            }
    
    async def optimize_for_detection(self, text: str, target_score: float = 0.1) -> str:
        """
        Optimize text to reduce AI detection score
        
        Args:
            text: Text to optimize
            target_score: Target AI detection score (lower is better)
            
        Returns:
            Optimized text
        """
        try:
            current_score = await self.check_ai_detection(text)
            
            if current_score <= target_score:
                return text  # Already good enough
            
            # Apply optimization techniques
            optimized_text = text
            
            # 1. Add more natural variations
            optimized_text = self._add_natural_variations(optimized_text)
            
            # 2. Break repetitive patterns
            optimized_text = self._break_repetitive_patterns(optimized_text)
            
            # 3. Add human-like imperfections
            optimized_text = self._add_human_imperfections(optimized_text)
            
            # 4. Vary sentence structure
            optimized_text = self._vary_sentence_structure(optimized_text)
            
            return optimized_text
            
        except Exception as e:
            logger.error(f"Failed to optimize for detection: {e}")
            return text
    
    def _add_natural_variations(self, text: str) -> str:
        """Add natural variations to reduce AI detection"""
        import random
        
        # Add occasional informal phrases
        informal_phrases = ["you know", "basically", "actually", "honestly", "like"]
        
        sentences = text.split('.')
        modified_sentences = []
        
        for sentence in sentences:
            if sentence.strip() and random.random() < 0.1:  # 10% chance
                phrase = random.choice(informal_phrases)
                sentence = f"{phrase}, {sentence.strip().lower()}"
            modified_sentences.append(sentence)
        
        return '. '.join(modified_sentences)
    
    def _break_repetitive_patterns(self, text: str) -> str:
        """Break repetitive patterns in the text"""
        import re
        
        # Replace repetitive sentence starters
        starters = ["Furthermore,", "Moreover,", "Additionally,", "In addition,"]
        alternatives = ["Also,", "Plus,", "What's more,", "On top of that,"]
        
        for i, starter in enumerate(starters):
            if starter in text:
                text = text.replace(starter, alternatives[i % len(alternatives)], 1)
        
        return text
    
    def _add_human_imperfections(self, text: str) -> str:
        """Add human-like imperfections"""
        import random
        
        # Occasionally add filler words
        filler_words = ["um", "uh", "well", "so", "right"]
        
        sentences = text.split('.')
        modified_sentences = []
        
        for sentence in sentences:
            if sentence.strip() and random.random() < 0.05:  # 5% chance
                filler = random.choice(filler_words)
                sentence = f"{filler}, {sentence.strip().lower()}"
            modified_sentences.append(sentence)
        
        return '. '.join(modified_sentences)
    
    def _vary_sentence_structure(self, text: str) -> str:
        """Vary sentence structure to appear more human"""
        import random
        
        sentences = text.split('.')
        modified_sentences = []
        
        for sentence in sentences:
            if sentence.strip() and len(sentence.split()) > 10:
                # Occasionally split long sentences
                if random.random() < 0.2:
                    words = sentence.split()
                    mid = len(words) // 2
                    sentence = f"{' '.join(words[:mid])}. {' '.join(words[mid:])}"
            
            modified_sentences.append(sentence)
        
        return '. '.join(modified_sentences) 