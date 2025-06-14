import asyncio
import time
import random
from typing import Tuple, List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HumanizationService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.initialized = False
        
        # Tone templates for different writing styles
        self.tone_templates = {
            "formal": {
                "sentence_starters": [
                    "Furthermore,", "Moreover,", "Additionally,", "In addition,",
                    "It should be emphasized that", "It is worth noting that", "Significantly,", "Notably,"
                ],
                "transition_phrases": [
                    "However,", "Nevertheless,", "On the other hand,", "In contrast,", "Conversely,",
                    "Despite this,", "Although,", "While,", "Whereas,"
                ],
                "conclusion_phrases": [
                    "In conclusion,", "To summarize,", "Overall,", "In summary,", "Therefore,",
                    "Thus,", "Hence,", "Consequently,", "As a result,"
                ]
            },
            "casual": {
                "sentence_starters": [
                    "You know,", "Actually,", "Basically,", "Honestly,", "To be honest,",
                    "I mean,", "Well,", "So,", "Like,", "Right,"
                ],
                "transition_phrases": [
                    "But,", "Though,", "However,", "On the flip side,", "That said,",
                    "At the same time,", "Still,", "Anyway,", "Plus,"
                ],
                "conclusion_phrases": [
                    "So yeah,", "Basically,", "In the end,", "Overall,", "To wrap it up,",
                    "Long story short,", "Bottom line,", "The thing is,"
                ]
            },
            "balanced": {
                "sentence_starters": [
                    "Additionally,", "Moreover,", "Furthermore,", "Also,", "Plus,",
                    "What's more,", "Not only that,", "On top of that,"
                ],
                "transition_phrases": [
                    "However,", "But,", "On the other hand,", "That said,", "Still,",
                    "Nevertheless,", "At the same time,", "Meanwhile,"
                ],
                "conclusion_phrases": [
                    "Overall,", "In conclusion,", "To summarize,", "So,", "Therefore,",
                    "As a result,", "In the end,", "Finally,"
                ]
            }
        }
        
        # Human writing patterns
        self.human_patterns = {
            "filler_words": ["um", "uh", "like", "you know", "basically", "actually", "honestly"],
            "contractions": ["don't", "can't", "won't", "isn't", "aren't", "doesn't", "didn't", "wouldn't"],
            "informal_phrases": ["kind of", "sort of", "a bit", "pretty much", "more or less"],
            "hedging": ["maybe", "perhaps", "possibly", "probably", "likely", "seems like"]
        }
        
    async def initialize(self):
        """Initialize the fine-tuned Llama 3 model"""
        if self.initialized:
            return
            
        try:
            logger.info("Initializing fine-tuned Llama 3 model...")
            
            # Load the fine-tuned model (you'll need to provide the actual model path)
            model_name = "meta-llama/Llama-2-7b-chat-hf"  # Replace with your fine-tuned model path
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.initialized = True
            logger.info("Fine-tuned Llama 3 model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Llama 3 model: {e}")
            # Fallback to rule-based humanization
            logger.info("Falling back to rule-based humanization")
            self.initialized = True
    
    async def humanize(self, text: str, tone: str = "balanced", 
                      preserve_meaning: bool = True) -> Tuple[str, float]:
        """
        Humanize the given text using fine-tuned Llama 3 and rule-based techniques
        
        Args:
            text: Input text to humanize
            tone: Desired tone (formal, casual, balanced)
            preserve_meaning: Whether to preserve the original meaning
            
        Returns:
            Tuple of (humanized_text, humanization_score)
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            start_time = time.time()
            
            # Step 1: Use fine-tuned model if available
            if self.model is not None:
                humanized_text = await self._model_based_humanization(text, tone, preserve_meaning)
            else:
                humanized_text = await self._rule_based_humanization(text, tone, preserve_meaning)
            
            # Step 2: Apply additional humanization techniques
            humanized_text = await self._apply_human_patterns(humanized_text, tone)
            
            # Step 3: Calculate humanization score
            humanization_score = await self._calculate_humanization_score(humanized_text, tone)
            
            processing_time = time.time() - start_time
            logger.info(f"Humanization completed in {processing_time:.2f}s with score {humanization_score:.2f}")
            
            return humanized_text, humanization_score
            
        except Exception as e:
            logger.error(f"Humanization failed: {e}")
            # Fallback: return original text with low score
            return text, 0.3
    
    async def _model_based_humanization(self, text: str, tone: str, preserve_meaning: bool) -> str:
        """Use fine-tuned Llama 3 model for humanization"""
        try:
            # Create prompt for the model
            prompt = self._create_humanization_prompt(text, tone, preserve_meaning)
            
            # Generate response
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs["input_ids"].shape[1] + 200,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the humanized text from response
            humanized_text = self._extract_humanized_text(response, text)
            
            return humanized_text if humanized_text else text
            
        except Exception as e:
            logger.error(f"Model-based humanization failed: {e}")
            return text
    
    async def _rule_based_humanization(self, text: str, tone: str, preserve_meaning: bool) -> str:
        """Rule-based humanization as fallback"""
        try:
            # Split into sentences
            sentences = self._split_into_sentences(text)
            humanized_sentences = []
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                    
                # Apply tone-specific transformations
                humanized_sentence = await self._apply_tone_transformations(sentence, tone)
                
                # Add variety to sentence structure
                humanized_sentence = await self._add_sentence_variety(humanized_sentence, i, tone)
                
                humanized_sentences.append(humanized_sentence)
            
            # Reconstruct text
            humanized_text = " ".join(humanized_sentences)
            
            # Post-process
            humanized_text = self._post_process_humanized_text(humanized_text, tone)
            
            return humanized_text
            
        except Exception as e:
            logger.error(f"Rule-based humanization failed: {e}")
            return text
    
    async def _apply_human_patterns(self, text: str, tone: str) -> str:
        """Apply human writing patterns to the text"""
        try:
            # Add contractions for casual tone
            if tone in ["casual", "balanced"]:
                text = self._add_contractions(text)
            
            # Add filler words occasionally (more for casual tone)
            if tone == "casual" and random.random() < 0.3:
                text = self._add_filler_words(text)
            
            # Add hedging phrases
            if random.random() < 0.2:
                text = self._add_hedging(text, tone)
            
            # Vary sentence length
            text = self._vary_sentence_length(text)
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to apply human patterns: {e}")
            return text
    
    def _create_humanization_prompt(self, text: str, tone: str, preserve_meaning: bool) -> str:
        """Create prompt for the fine-tuned model"""
        tone_description = {
            "formal": "formal and professional",
            "casual": "casual and conversational", 
            "balanced": "natural and balanced"
        }
        
        prompt = f"""Task: Convert the following AI-generated text into {tone_description.get(tone, 'natural')} human writing.

Original text: "{text}"

Requirements:
- Maintain the same meaning and key information
- Make it sound more human and natural
- Use {tone} tone and style
- Avoid repetitive patterns
- Add natural variations in sentence structure

Humanized version:"""
        
        return prompt
    
    def _extract_humanized_text(self, response: str, original_text: str) -> str:
        """Extract humanized text from model response"""
        try:
            # Look for the humanized version in the response
            if "Humanized version:" in response:
                parts = response.split("Humanized version:")
                if len(parts) > 1:
                    return parts[1].strip()
            
            # Fallback: return the last part of the response
            lines = response.split('\n')
            for line in reversed(lines):
                if line.strip() and len(line.strip()) > len(original_text) * 0.5:
                    return line.strip()
            
            return original_text
            
        except Exception as e:
            logger.error(f"Failed to extract humanized text: {e}")
            return original_text
    
    async def _apply_tone_transformations(self, sentence: str, tone: str) -> str:
        """Apply tone-specific transformations to a sentence"""
        try:
            templates = self.tone_templates.get(tone, self.tone_templates["balanced"])
            
            # Randomly add tone-appropriate phrases
            if random.random() < 0.3:
                if random.random() < 0.5:
                    starter = random.choice(templates["sentence_starters"])
                    sentence = f"{starter} {sentence.lower()}"
                else:
                    transition = random.choice(templates["transition_phrases"])
                    sentence = f"{transition} {sentence.lower()}"
            
            return sentence
            
        except Exception as e:
            logger.error(f"Failed to apply tone transformations: {e}")
            return sentence
    
    async def _add_sentence_variety(self, sentence: str, index: int, tone: str) -> str:
        """Add variety to sentence structure"""
        try:
            # Occasionally change sentence structure
            if random.random() < 0.2:
                # Split long sentences
                if len(sentence.split()) > 15:
                    words = sentence.split()
                    mid = len(words) // 2
                    sentence = f"{' '.join(words[:mid])}. {' '.join(words[mid:])}"
            
            return sentence
            
        except Exception as e:
            logger.error(f"Failed to add sentence variety: {e}")
            return sentence
    
    def _add_contractions(self, text: str) -> str:
        """Add contractions to make text more casual"""
        contractions_map = {
            "do not": "don't",
            "cannot": "can't", 
            "will not": "won't",
            "is not": "isn't",
            "are not": "aren't",
            "does not": "doesn't",
            "did not": "didn't",
            "would not": "wouldn't",
            "could not": "couldn't",
            "should not": "shouldn't"
        }
        
        for formal, contraction in contractions_map.items():
            text = re.sub(r'\b' + formal + r'\b', contraction, text, flags=re.IGNORECASE)
        
        return text
    
    def _add_filler_words(self, text: str) -> str:
        """Add occasional filler words"""
        sentences = self._split_into_sentences(text)
        modified_sentences = []
        
        for sentence in sentences:
            if random.random() < 0.1:  # 10% chance
                filler = random.choice(self.human_patterns["filler_words"])
                sentence = f"{filler}, {sentence.lower()}"
            modified_sentences.append(sentence)
        
        return " ".join(modified_sentences)
    
    def _add_hedging(self, text: str, tone: str) -> str:
        """Add hedging phrases to make text more human"""
        if tone == "formal":
            hedges = ["perhaps", "possibly", "likely", "seems to"]
        else:
            hedges = ["maybe", "probably", "kind of", "sort of"]
        
        sentences = self._split_into_sentences(text)
        modified_sentences = []
        
        for sentence in sentences:
            if random.random() < 0.15:  # 15% chance
                hedge = random.choice(hedges)
                sentence = f"{sentence} {hedge}."
            modified_sentences.append(sentence)
        
        return " ".join(modified_sentences)
    
    def _vary_sentence_length(self, text: str) -> str:
        """Vary sentence length for more natural flow"""
        sentences = self._split_into_sentences(text)
        modified_sentences = []
        
        for sentence in sentences:
            # Occasionally combine short sentences or split long ones
            if len(sentence.split()) < 5 and random.random() < 0.3:
                # Try to combine with next sentence
                pass
            elif len(sentence.split()) > 20 and random.random() < 0.3:
                # Split long sentence
                words = sentence.split()
                mid = len(words) // 2
                sentence = f"{' '.join(words[:mid])}. {' '.join(words[mid:])}"
            
            modified_sentences.append(sentence)
        
        return " ".join(modified_sentences)
    
    def _post_process_humanized_text(self, text: str, tone: str) -> str:
        """Post-process humanized text"""
        # Fix spacing and punctuation
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)
        
        # Ensure proper capitalization
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    async def _calculate_humanization_score(self, text: str, tone: str) -> float:
        """Calculate how human-like the text is"""
        try:
            score = 0.0
            
            # Check for contractions (good for casual/balanced)
            contractions_count = sum(1 for contraction in self.human_patterns["contractions"] 
                                   if contraction in text.lower())
            score += min(0.2, contractions_count * 0.05)
            
            # Check for natural sentence length variation
            sentences = self._split_into_sentences(text)
            if len(sentences) > 1:
                lengths = [len(s.split()) for s in sentences]
                length_variance = sum((l - sum(lengths)/len(lengths))**2 for l in lengths) / len(lengths)
                score += min(0.2, length_variance * 0.01)
            
            # Check for tone-appropriate phrases
            templates = self.tone_templates.get(tone, self.tone_templates["balanced"])
            tone_phrases = templates["sentence_starters"] + templates["transition_phrases"]
            tone_matches = sum(1 for phrase in tone_phrases if phrase.lower() in text.lower())
            score += min(0.2, tone_matches * 0.05)
            
            # Check for natural word patterns
            words = text.lower().split()
            if len(words) > 10:
                # Check for common word patterns
                common_patterns = ["the", "and", "to", "of", "a", "in", "is", "it", "you", "that"]
                pattern_matches = sum(1 for word in words if word in common_patterns)
                score += min(0.2, (pattern_matches / len(words)) * 0.5)
            
            # Base score for any humanization
            score += 0.4
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Failed to calculate humanization score: {e}")
            return 0.5 