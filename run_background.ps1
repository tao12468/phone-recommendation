$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\pythonw.exe"
$workDir = Join-Path $root "code"

Start-Process `
    -FilePath $python `
    -ArgumentList "app.py" `
    -WorkingDirectory $workDir `
    -WindowStyle Hidden
