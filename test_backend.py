import requests
import json

def test_backend():
    """Test the backend API endpoints"""
    
    # Test data
    test_text = "The implementation of artificial intelligence technologies has revolutionized various industries. Furthermore, machine learning algorithms have demonstrated remarkable capabilities in processing large datasets. Additionally, natural language processing systems have significantly improved human-computer interactions."
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing AI-to-Human Converter Backend")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: PASSED")
        else:
            print("❌ Health check: FAILED")
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
        return
    
    # Test 2: Grammar correction
    try:
        response = requests.post(
            f"{base_url}/api/grammar",
            json={"text": test_text}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Grammar correction: PASSED ({data.get('corrections_made', 0)} corrections)")
        else:
            print(f"❌ Grammar correction: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ Grammar correction: ERROR - {e}")
    
    # Test 3: Humanization
    try:
        response = requests.post(
            f"{base_url}/api/humanize",
            json={"text": test_text, "tone": "balanced"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Humanization: PASSED (Score: {data.get('humanization_score', 0):.2f})")
        else:
            print(f"❌ Humanization: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ Humanization: ERROR - {e}")
    
    # Test 4: AI Detection
    try:
        response = requests.post(
            f"{base_url}/api/detect",
            json={"text": test_text}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Detection: PASSED (Score: {data.get('ai_detection_score', 0):.2f})")
        else:
            print(f"❌ AI Detection: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ AI Detection: ERROR - {e}")
    
    # Test 5: Plagiarism check
    try:
        response = requests.post(
            f"{base_url}/api/plagiarism",
            json={"text": test_text}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Plagiarism check: PASSED (Score: {data.get('plagiarism_score', 0):.2f})")
        else:
            print(f"❌ Plagiarism check: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ Plagiarism check: ERROR - {e}")
    
    # Test 6: Full conversion
    try:
        response = requests.post(
            f"{base_url}/api/convert",
            json={
                "text": test_text,
                "tone": "balanced",
                "preserve_meaning": True,
                "check_plagiarism": True,
                "check_ai_detection": True
            }
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Full conversion: PASSED")
            print(f"   - Original length: {len(test_text)} chars")
            print(f"   - Converted length: {len(data.get('converted_text', ''))} chars")
            print(f"   - Grammar corrections: {data.get('grammar_corrections', 0)}")
            print(f"   - Humanization score: {data.get('humanization_score', 0):.2f}")
            print(f"   - AI detection score: {data.get('ai_detection_score', 0):.2f}")
            print(f"   - Plagiarism score: {data.get('plagiarism_score', 0):.2f}")
            print(f"   - Confidence: {data.get('confidence', 0):.2f}")
            print(f"   - Processing time: {data.get('processing_time', 0):.2f}s")
            
            # Show sample of converted text
            converted = data.get('converted_text', '')
            if converted:
                print(f"   - Sample output: {converted[:100]}...")
        else:
            print(f"❌ Full conversion: FAILED - {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Full conversion: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")

if __name__ == "__main__":
    test_backend() 