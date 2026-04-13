# STC ALGO Backend

Behavioral analysis engine powered by Gemini 2.0 Flash.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your API key in `.env`:
   ```text
   GEMINI_API_KEY=your_key_here
   ```

3. Run the server:
   ```bash
   python app.py
   ```

## Testing

Use the following curl command to test the `/analyze` endpoint:

```bash
curl -X POST http://localhost:5010/analyze \
  -H "Content-Type: application/json" \
  -d '{"input": "Indian teenager buys minimal phone covers every 3 weeks"}'
```
