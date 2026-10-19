$ErrorActionPreference = 'Stop'
python (Join-Path $PSScriptRoot 'create_submission_audio.py')
if ($LASTEXITCODE -ne 0) { throw "Neural narration generation failed with exit code $LASTEXITCODE" }
python (Join-Path $PSScriptRoot 'create_submission_video.py')
if ($LASTEXITCODE -ne 0) { throw "Video rendering failed with exit code $LASTEXITCODE" }
