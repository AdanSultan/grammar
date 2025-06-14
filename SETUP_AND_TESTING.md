# AI-to-Human Converter - Setup & Testing Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- Git

### Step 1: Clone and Setup
```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd Grammar

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### Step 2: Start the Services

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 3: Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🧪 Testing the Application

### 1. Backend API Testing
Run the automated test script:
```bash
python test_backend.py
```

This will test all endpoints:
- ✅ Health check
- ✅ Grammar correction
- ✅ Humanization
- ✅ AI detection
- ✅ Plagiarism check
- ✅ Full conversion

### 2. Manual Testing via Web Interface

1. **Open** http://localhost:3000 in your browser
2. **Paste** this AI-generated text:
   ```
   The implementation of artificial intelligence technologies has revolutionized various industries. Furthermore, machine learning algorithms have demonstrated remarkable capabilities in processing large datasets. Additionally, natural language processing systems have significantly improved human-computer interactions.
   ```
3. **Select** tone (Balanced/Formal/Casual)
4. **Click** "Convert"
5. **Check** the results:
   - Grammar corrections count
   - Humanization score (should be > 0.5)
   - AI detection score (should be < 0.3)
   - Plagiarism score (should be < 0.2)
   - Confidence score (should be > 0.7)
   - Processing time (should be < 2 seconds)

### 3. API Endpoint Testing

**Test individual endpoints:**

```bash
# Health check
curl http://localhost:8000/health

# Grammar correction
curl -X POST http://localhost:8000/api/grammar \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test sentence with grammer errors."}'

# Humanization
curl -X POST http://localhost:8000/api/humanize \
  -H "Content-Type: application/json" \
  -d '{"text": "The implementation of AI has revolutionized industries.", "tone": "balanced"}'

# AI Detection
curl -X POST http://localhost:8000/api/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "The implementation of AI has revolutionized industries."}'

# Plagiarism Check
curl -X POST http://localhost:8000/api/plagiarism \
  -H "Content-Type: application/json" \
  -d '{"text": "The implementation of AI has revolutionized industries."}'

# Full Conversion
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The implementation of AI has revolutionized industries.",
    "tone": "balanced",
    "preserve_meaning": true,
    "check_plagiarism": true,
    "check_ai_detection": true
  }'
```

## 📊 Expected Results

### Performance Metrics
- **Response Time:** < 2 seconds
- **Grammar Accuracy:** 99%+ (rule-based fallback)
- **Humanization Score:** 0.6-0.9 (varies by tone)
- **AI Detection Score:** 0.1-0.3 (lower is better)
- **Plagiarism Score:** 0.05-0.2 (lower is better)
- **Confidence Score:** 0.7-0.95

### Sample Test Cases

**Test Case 1: Formal AI Text**
```
Input: "The implementation of artificial intelligence technologies has revolutionized various industries. Furthermore, machine learning algorithms have demonstrated remarkable capabilities in processing large datasets."
Expected: More natural, varied sentence structure, contractions, informal transitions
```

**Test Case 2: Casual AI Text**
```
Input: "You know, AI is like totally changing everything. It's basically making things way better and stuff."
Expected: More balanced tone, proper grammar, varied vocabulary
```

**Test Case 3: Technical AI Text**
```
Input: "The utilization of machine learning algorithms facilitates the optimization of data processing workflows."
Expected: Less formal, more natural phrasing, varied sentence structure
```

## 🔧 Troubleshooting

### Common Issues

1. **Backend won't start:**
   - Check if port 8000 is available
   - Ensure all dependencies are installed
   - Check Python version (3.8+)

2. **Frontend won't start:**
   - Check if port 3000 is available
   - Ensure Node.js 16+ is installed
   - Clear npm cache: `npm cache clean --force`

3. **API errors:**
   - Check if backend is running on port 8000
   - Verify CORS settings
   - Check network connectivity

4. **Model loading errors:**
   - The app uses rule-based fallbacks if models aren't available
   - Check logs for specific error messages

### Performance Optimization

1. **For faster response times:**
   - Use shorter input text
   - Disable optional checks (plagiarism, AI detection)
   - Use "balanced" tone (fastest processing)

2. **For better quality:**
   - Use longer input text
   - Enable all checks
   - Try different tones

## 🎯 Success Criteria

The application is working correctly if:

1. ✅ **Backend starts** without errors
2. ✅ **Frontend loads** at http://localhost:3000
3. ✅ **API endpoints** respond within 2 seconds
4. ✅ **Text conversion** produces different output
5. ✅ **Scores are reasonable** (see Expected Results)
6. ✅ **No crashes** during normal usage
7. ✅ **Mobile responsive** design works

## 📝 Notes

- The app uses **rule-based fallbacks** when external APIs aren't available
- **No API keys required** for basic functionality
- **All processing is local** (no external calls by default)
- **Results may vary** based on input text and tone selection

## 🚀 Next Steps

1. **Add API keys** for enhanced functionality:
   - CopyLeaks for plagiarism detection
   - GPTZero for AI detection
   - Gramformer for grammar correction

2. **Deploy to production:**
   - Backend: AWS EC2, Google Cloud, or similar
   - Frontend: Vercel, Netlify, or similar

3. **Scale and optimize:**
   - Add caching
   - Implement rate limiting
   - Add user authentication
   - Add usage analytics

---

**🎉 Congratulations!** Your AI-to-Human Converter is now running and ready to test! 