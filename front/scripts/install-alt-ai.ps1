# install-alt-ai.ps1 — Windows / PowerShell installer for the local
# Ollama-based alt-text generator. For Bash shells, use install-alt-ai.sh.
#
# Installs (if missing): Ollama (via winget).
# Pulls: gemma4:e2b  (override with the OLLAMA_MODEL env var).
#
# After this script finishes, generate alt text with:
#   node front\scripts\alt-from-ollama.mjs path\to\image.jpg
#
# Run as:
#   powershell -ExecutionPolicy Bypass -File install-alt-ai.ps1

$ErrorActionPreference = 'Stop'

$Base  = if ($env:OLLAMA_MODEL_BASE) { $env:OLLAMA_MODEL_BASE } else { 'gemma4:e2b' }
$Model = if ($env:OLLAMA_MODEL)      { $env:OLLAMA_MODEL }      else { $Base }

Write-Host "→ Platform: Windows $env:PROCESSOR_ARCHITECTURE"
Write-Host "→ Target model: $Model"

# 1. Install Ollama if missing.
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "→ Installing Ollama via winget…"
    winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements
    # The new install puts ollama on PATH after a shell reload.
    $env:PATH = "$env:PATH;$env:LOCALAPPDATA\Programs\Ollama"
  } else {
    Write-Error "winget not found. Install Ollama manually from https://ollama.com/download, then re-run this script."
  }
}

# 2. Make sure the daemon is up.
$daemonUp = $false
try {
  $null = ollama list 2>$null
  if ($LASTEXITCODE -eq 0) { $daemonUp = $true }
} catch { $daemonUp = $false }

if (-not $daemonUp) {
  Write-Host "→ Starting the Ollama daemon in the background…"
  Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden
  for ($i = 1; $i -le 10; $i++) {
    Start-Sleep -Seconds 1
    try {
      $null = ollama list 2>$null
      if ($LASTEXITCODE -eq 0) { $daemonUp = $true; break }
    } catch {}
  }
  if (-not $daemonUp) {
    Write-Error "Ollama did not start in 10 seconds."
  }
}

# 3. Pull the model if missing.
$present = ollama list | Select-Object -Skip 1 | ForEach-Object { ($_ -split '\s+')[0] }
if ($present -contains $Model) {
  Write-Host "→ $Model already present."
} else {
  Write-Host "→ Pulling $Model …"
  ollama pull $Model
  if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Could not pull `"$Model`". Check your network connection and the model tag." -ForegroundColor Yellow
    Write-Host "To try a different on-device vision model, set OLLAMA_MODEL and re-run, e.g.:" -ForegroundColor Yellow
    Write-Host "    `$env:OLLAMA_MODEL='gemma3n:e2b'; powershell -ExecutionPolicy Bypass -File install-alt-ai.ps1" -ForegroundColor Yellow
    Write-Host "Browse tags at https://ollama.com/library" -ForegroundColor Yellow
    exit 1
  }
}

Write-Host "→ Ready. Test with:"
Write-Host "    node front\scripts\alt-from-ollama.mjs C:\path\to\image.jpg"
