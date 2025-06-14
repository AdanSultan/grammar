import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

class TestAPIEndpoints:
    """Test suite for AI-to-Human Converter API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "grammar" in data["services"]
        assert "humanization" in data["services"]
        assert "detection" in data["services"]
        assert "plagiarism" in data["services"]
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "AI-to-Human Converter API" in data["message"]
        assert data["status"] == "active"
    
    def test_grammar_correction(self):
        """Test grammar correction endpoint"""
        test_text = "This is a test sentence with grammer errors and bad punctuation"
        response = client.post("/api/grammar", json={"text": test_text})
        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "corrected_text" in data
        assert "corrections_made" in data
        assert data["status"] == "success"
        assert data["original_text"] == test_text
        assert len(data["corrected_text"]) > 0
    
    def test_humanization(self):
        """Test humanization endpoint"""
        test_text = "The implementation of artificial intelligence technologies has revolutionized various industries."
        response = client.post("/api/humanize", json={
            "text": test_text,
            "tone": "balanced"
        })
        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "humanized_text" in data
        assert "humanization_score" in data
        assert data["status"] == "success"
        assert data["original_text"] == test_text
        assert len(data["humanized_text"]) > 0
        assert 0 <= data["humanization_score"] <= 1
    
    def test_ai_detection(self):
        """Test AI detection endpoint"""
        test_text = "The implementation of artificial intelligence technologies has revolutionized various industries."
        response = client.post("/api/detect", json={"text": test_text})
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "ai_detection_score" in data
        assert "is_ai_detected" in data
        assert data["status"] == "success"
        assert data["text"] == test_text
        assert 0 <= data["ai_detection_score"] <= 1
        assert isinstance(data["is_ai_detected"], bool)
    
    def test_plagiarism_check(self):
        """Test plagiarism check endpoint"""
        test_text = "The implementation of artificial intelligence technologies has revolutionized various industries."
        response = client.post("/api/plagiarism", json={"text": test_text})
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "plagiarism_score" in data
        assert "is_plagiarized" in data
        assert data["status"] == "success"
        assert data["text"] == test_text
        assert 0 <= data["plagiarism_score"] <= 1
        assert isinstance(data["is_plagiarized"], bool)
    
    def test_full_conversion(self):
        """Test full conversion endpoint"""
        test_text = "The implementation of artificial intelligence technologies has revolutionized various industries. Furthermore, machine learning algorithms have demonstrated remarkable capabilities."
        response = client.post("/api/convert", json={
            "text": test_text,
            "tone": "balanced",
            "preserve_meaning": True,
            "check_plagiarism": True,
            "check_ai_detection": True
        })
        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "converted_text" in data
        assert "grammar_corrections" in data
        assert "humanization_score" in data
        assert "ai_detection_score" in data
        assert "plagiarism_score" in data
        assert "processing_time" in data
        assert "confidence" in data
        assert data["original_text"] == test_text
        assert len(data["converted_text"]) > 0
        assert data["grammar_corrections"] >= 0
        assert 0 <= data["humanization_score"] <= 1
        assert 0 <= data["ai_detection_score"] <= 1
        assert 0 <= data["plagiarism_score"] <= 1
        assert data["processing_time"] > 0
        assert 0 <= data["confidence"] <= 1
    
    def test_different_tones(self):
        """Test humanization with different tones"""
        test_text = "The implementation of artificial intelligence technologies has revolutionized various industries."
        tones = ["formal", "casual", "balanced"]
        
        for tone in tones:
            response = client.post("/api/humanize", json={
                "text": test_text,
                "tone": tone
            })
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert len(data["humanized_text"]) > 0
    
    def test_empty_text(self):
        """Test handling of empty text"""
        response = client.post("/api/convert", json={"text": ""})
        assert response.status_code == 422  # Validation error
    
    def test_large_text(self):
        """Test handling of large text"""
        large_text = "This is a test sentence. " * 100  # 2500 characters
        response = client.post("/api/convert", json={
            "text": large_text,
            "tone": "balanced"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["converted_text"]) > 0
    
    def test_special_characters(self):
        """Test handling of special characters"""
        special_text = "This text has special chars: @#$%^&*()_+{}|:<>?[]\\;'\"`~"
        response = client.post("/api/convert", json={
            "text": special_text,
            "tone": "balanced"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["converted_text"]) > 0
    
    def test_unicode_text(self):
        """Test handling of unicode text"""
        unicode_text = "This text has unicode: émojis 🚀 and accénts"
        response = client.post("/api/convert", json={
            "text": unicode_text,
            "tone": "balanced"
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["converted_text"]) > 0

class TestPerformance:
    """Test performance requirements"""
    
    def test_response_time(self):
        """Test that response time is under 2 seconds"""
        import time
        test_text = "The implementation of artificial intelligence technologies has revolutionized various industries."
        
        start_time = time.time()
        response = client.post("/api/convert", json={
            "text": test_text,
            "tone": "balanced"
        })
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Under 2 seconds
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        test_text = "The implementation of artificial intelligence technologies."
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.post("/api/convert", json={
                    "text": test_text,
                    "tone": "balanced"
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Start 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert all(status == 200 for status in results)

class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        response = client.post("/api/convert", data="invalid json")
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post("/api/convert", json={})
        assert response.status_code == 422
    
    def test_invalid_tone(self):
        """Test handling of invalid tone"""
        response = client.post("/api/convert", json={
            "text": "test",
            "tone": "invalid_tone"
        })
        # Should still work with fallback to balanced
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 