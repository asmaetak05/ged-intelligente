$ErrorActionPreference = "Stop"

Write-Host "Running tests..."
.venv\Scripts\Activate.ps1
pytest --cov=backend --cov=nlp --cov=ocr --cov=ml --cov-report=term-missing

if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "Tests failed!" -ForegroundColor Red
}
