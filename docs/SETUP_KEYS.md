# Keys and accounts you must create (free tiers)

I cannot open your Devpost, Google, or Parallel accounts from this environment. Create these on the same email you use for the hackathon.

## 1. Devpost

https://agentic-cinema.devpost.com/  
Join the hackathon. At submit time pick **Parallel**.

## 2. Gemini

- Fast path: https://aistudio.google.com/app/apikey → `GEMINI_API_KEY`
- Production path: Google Cloud project + Vertex AI API + Agent Engine  
  Credits form is linked from the hackathon resources page.

`GOOGLE_GENAI_USE_VERTEXAI=true` plus `GOOGLE_CLOUD_PROJECT` switches the client to Vertex.

## 3. Parallel

https://platform.parallel.ai  
Signup grants hackathon credits (typically $20–$80). No promo code required.  
Put the key in `PARALLEL_API_KEY`.

## 4. Hosting

```bash
gcloud run deploy qissa-studio --source . --region us-central1 --allow-unauthenticated
```

The hosted URL goes on the Devpost form.

## 5. Video

Follow `docs/DEMO_SCRIPT.md`. Public YouTube/Vimeo, English, ≤3 minutes, app on camera.
