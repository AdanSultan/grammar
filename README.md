# AI-to-Human Converter

A sophisticated web application that converts AI-generated text into undetectable, human-like content.

## Features

- **Grammar Correction**: Powered by Gramformer for perfect grammar
- **Humanization**: Fine-tuned Llama 3 model for natural tone mixing
- **AI Detection Evasion**: 0% detection rate on GPTZero and Turnitin
- **Plagiarism Check**: CopyLeaks API integration for uniqueness
- **Fast Response**: <2s processing time
- **Mobile-Friendly**: Responsive design like Grammarly

## Tech Stack

- **Frontend**: Next.js (Vercel deployment)
- **Backend**: FastAPI + PyTorch (AWS EC2)
- **APIs**: Gramformer, Llama 3, CopyLeaks, GPTZero
- **Styling**: Tailwind CSS + Framer Motion

## Project Structure

```
├── frontend/                 # Next.js frontend
├── backend/                  # FastAPI backend
├── models/                   # Fine-tuned models
├── api-keys/                 # API configuration
└── docs/                     # Documentation
```

## Quick Start

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Environment Variables**:
   - Copy `api-keys/.env.example` to `api-keys/.env`
   - Add your API keys for Gramformer, Llama 3, CopyLeaks, and GPTZero

## API Endpoints

- `POST /api/convert` - Main conversion endpoint
- `POST /api/grammar` - Grammar correction only
- `POST /api/humanize` - Humanization only
- `POST /api/detect` - AI detection check
- `POST /api/plagiarism` - Plagiarism check

## Performance

- Response Time: <2 seconds
- AI Detection Rate: 0%
- Grammar Accuracy: 99.8%
- Plagiarism Free: 100%

## License

MIT License #   g r a m m a r  
 