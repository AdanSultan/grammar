import asyncio
import time
from typing import Tuple, List, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqGeneration
from gramformer import Gramformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrammarService:
    def __init__(self):
        self.gramformer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.initialized = False
        
    async def initialize(self):
        """Initialize Gramformer model asynchronously"""
        if self.initialized:
            return
            
        try:
            logger.info("Initializing Gramformer...")
            # Initialize Gramformer with correction model
            self.gramformer = Gramformer(models=1, use_gpu=torch.cuda.is_available())
            self.initialized = True
            logger.info("Gramformer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gramformer: {e}")
            raise
    
    async def correct_grammar(self, text: str) -> Tuple[str, int]:
        """
        Correct grammar in the given text using Gramformer
        
        Args:
            text: Input text to correct
            
        Returns:
            Tuple of (corrected_text, number_of_corrections)
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            start_time = time.time()
            
            # Split text into sentences for better processing
            sentences = self._split_into_sentences(text)
            corrected_sentences = []
            total_corrections = 0
            
            for sentence in sentences:
                if sentence.strip():
                    # Get corrections from Gramformer
                    corrections = self.gramformer.correct(sentence)
                    
                    if corrections and len(corrections) > 0:
                        corrected_sentence = corrections[0]
                        # Count differences to estimate corrections
                        corrections_made = self._count_corrections(sentence, corrected_sentence)
                        total_corrections += corrections_made
                        corrected_sentences.append(corrected_sentence)
                    else:
                        corrected_sentences.append(sentence)
            
            # Reconstruct the text
            corrected_text = " ".join(corrected_sentences)
            
            # Post-process to ensure proper spacing and punctuation
            corrected_text = self._post_process_text(corrected_text)
            
            processing_time = time.time() - start_time
            logger.info(f"Grammar correction completed in {processing_time:.2f}s with {total_corrections} corrections")
            
            return corrected_text, total_corrections
            
        except Exception as e:
            logger.error(f"Grammar correction failed: {e}")
            # Fallback: return original text with 0 corrections
            return text, 0
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for better grammar correction"""
        import re
        
        # Simple sentence splitting - can be improved with NLTK
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _count_corrections(self, original: str, corrected: str) -> int:
        """Estimate number of corrections made"""
        import difflib
        
        # Use difflib to find differences
        matcher = difflib.SequenceMatcher(None, original, corrected)
        differences = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ['replace', 'delete', 'insert']:
                differences += 1
        
        return differences
    
    def _post_process_text(self, text: str) -> str:
        """Post-process corrected text for better formatting"""
        import re
        
        # Fix common spacing issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)  # Remove spaces before punctuation
        text = re.sub(r'([.!?,;:])\s*([A-Z])', r'\1 \2', text)  # Add space after punctuation before capital
        
        # Fix capitalization
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    async def get_grammar_suggestions(self, text: str) -> List[Dict[str, Any]]:
        """
        Get detailed grammar suggestions for the text
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of grammar suggestions with details
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            suggestions = []
            sentences = self._split_into_sentences(text)
            
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    corrections = self.gramformer.correct(sentence)
                    
                    if corrections and len(corrections) > 0:
                        corrected = corrections[0]
                        if corrected != sentence:
                            suggestions.append({
                                "sentence_index": i,
                                "original": sentence,
                                "corrected": corrected,
                                "suggestion": f"Consider: '{corrected}'"
                            })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get grammar suggestions: {e}")
            return []
    
    async def check_grammar_quality(self, text: str) -> Dict[str, float]:
        """
        Check overall grammar quality of the text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            # Get suggestions
            suggestions = await self.get_grammar_suggestions(text)
            
            # Calculate metrics
            total_sentences = len(self._split_into_sentences(text))
            sentences_with_errors = len(suggestions)
            
            if total_sentences == 0:
                return {
                    "grammar_score": 1.0,
                    "error_rate": 0.0,
                    "suggestions_count": 0
                }
            
            error_rate = sentences_with_errors / total_sentences
            grammar_score = max(0.0, 1.0 - error_rate)
            
            return {
                "grammar_score": grammar_score,
                "error_rate": error_rate,
                "suggestions_count": len(suggestions)
            }
            
        except Exception as e:
            logger.error(f"Failed to check grammar quality: {e}")
            return {
                "grammar_score": 0.0,
                "error_rate": 1.0,
                "suggestions_count": 0
            } 