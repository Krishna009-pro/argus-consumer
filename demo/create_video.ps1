param(
    [string]$Output = "$PSScriptRoot\ARGUS-Consumer-Prototype-Demo.mp4"
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.Rate = -1
$wav = Join-Path $PSScriptRoot 'narration.wav'
$speaker.SetOutputToWaveFile($wav)
@(
    'ARGUS Consumer is a public-data research prototype for consumer and retail financial signals.'
    'Target: company name, public sources, comparable history, challenge, evidence report. Live source discovery remains.'
    'Import an annual report locally. ARGUS caches and hashes it, then proposes page-linked figures.'
    'Reviewers check values, units, periods, statement basis and scope. Uncertain rows stay unresolved.'
    'Verified observations feed deterministic calculations. Persistence and evidence gates stay unchanged.'
    'For HUL, twelve figures were visually checked on PDF pages 138, 139, 183 and 184. Continuing revenue: standalone 61,975 crore in fiscal 2026 and 59,676 in fiscal 2025; consolidated 64,468 and 61,328. Page and file hash are retained.'
    'ARGUS abstains: two revenue years versus the six-period gate; volume and eligible peers are missing. Balance sheets split around the demerger. No finding was generated. Six of 56 extracted note-number errors were rejected; fifty remain unverified.'
    'Twenty-four tests pass, dashboard health is okay, and thresholds are unchanged. This is a prototype, not a live discovery system. Longer comparable histories remain to be built.'
) | ForEach-Object { $speaker.Speak($_) }
$speaker.Dispose()
python (Join-Path $PSScriptRoot 'create_video.py') --narration $wav --output $Output
if ($LASTEXITCODE -ne 0) { throw "Video rendering failed with exit code $LASTEXITCODE" }
Write-Host "Video: $Output"
