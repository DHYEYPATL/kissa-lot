$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   Qissa Studio: Cloud Run Deployer     " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Check Project
$PROJECT_ID = (gcloud config get-value project 2>$null)
if (-not $PROJECT_ID -or $PROJECT_ID -eq "(unset)") {
    Write-Host "Setting project to citric-energy-475702-d6..." -ForegroundColor Yellow
    gcloud config set project citric-energy-475702-d6
    $PROJECT_ID = "citric-energy-475702-d6"
}
Write-Host "[+] GCP Project: $PROJECT_ID" -ForegroundColor Green

# 2. Check & Enable APIs
Write-Host "[+] Enabling required GCP services..." -ForegroundColor Yellow
try {
    gcloud services enable `
        run.googleapis.com `
        cloudbuild.googleapis.com `
        artifactregistry.googleapis.com `
        aiplatform.googleapis.com `
        secretmanager.googleapis.com
    Write-Host "[+] All GCP APIs enabled successfully." -ForegroundColor Green
} catch {
    Write-Host "[!] Could not enable APIs. Please make sure billing/coupon is linked at: https://console.cloud.google.com/billing" -ForegroundColor Red
    exit 1
}

# 3. Handle Secrets (.env or Prompt)
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match "^\s*GEMINI_API_KEY\s*=\s*(.+)$") {
            $Env:GEMINI_API_KEY = $matches[1].Trim()
        }
        if ($_ -match "^\s*PARALLEL_API_KEY\s*=\s*(.+)$") {
            $Env:PARALLEL_API_KEY = $matches[1].Trim()
        }
    }
}

if (-not $Env:GEMINI_API_KEY) {
    $Env:GEMINI_API_KEY = Read-Host "Enter your GEMINI_API_KEY (from https://aistudio.google.com/app/apikey)"
}
if (-not $Env:PARALLEL_API_KEY) {
    $Env:PARALLEL_API_KEY = Read-Host "Enter your PARALLEL_API_KEY (from https://platform.parallel.ai)"
}

Write-Host "[+] Setting up Secret Manager..." -ForegroundColor Yellow
try {
    $Env:GEMINI_API_KEY | gcloud secrets create GEMINI_API_KEY --data-file=- 2>$null
} catch {
    $Env:GEMINI_API_KEY | gcloud secrets versions add GEMINI_API_KEY --data-file=-
}

try {
    $Env:PARALLEL_API_KEY | gcloud secrets create PARALLEL_API_KEY --data-file=- 2>$null
} catch {
    $Env:PARALLEL_API_KEY | gcloud secrets versions add PARALLEL_API_KEY --data-file=-
}

$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding GEMINI_API_KEY `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" 2>$null

gcloud secrets add-iam-policy-binding PARALLEL_API_KEY `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" 2>$null

Write-Host "[+] Secrets configured." -ForegroundColor Green

# 4. Deploy to Cloud Run
Write-Host "[+] Deploying qissa-studio to Cloud Run (Region: us-central1)..." -ForegroundColor Yellow
gcloud run deploy qissa-studio `
    --source . `
    --region us-central1 `
    --allow-unauthenticated `
    --port 8080 `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --min-instances 0 `
    --max-instances 3 `
    --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest,PARALLEL_API_KEY=PARALLEL_API_KEY:latest" `
    --set-env-vars="GEMINI_MODEL=gemini-2.5-flash,PARALLEL_SEARCH_MODE=fast,KISSA_DEMO_MODE=false,GOOGLE_CLOUD_LOCATION=us-central1" `
    --quiet

Write-Host "=========================================" -ForegroundColor Green
Write-Host "   DEPLOYMENT COMPLETE!                 " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
$SERVICE_URL = (gcloud run services describe qissa-studio --region us-central1 --format='value(status.url)')
Write-Host "Live Hosted URL for Devpost: $SERVICE_URL" -ForegroundColor Cyan
