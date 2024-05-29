# python venv creation
python -m venv .env
./.env/Scripts/activate.ps1

# python lib installation
pip install -r requirements.txt

# key generation

$sshKeyPath = "$PSScriptRoot\.ssh"

if (-not (Test-Path -Path $sshKeyPath)) {
    New-Item -Path $sshKeyPath -ItemType Directory
}

$sshKeyGen = New-Object System.Diagnostics.ProcessStartInfo
$sshKeyGen.FileName = "ssh-keygen.exe"
$sshKeyGen.Arguments = "-f $sshKeyPath"
$sshKeyGen.WorkingDirectory = $sshKeyPath
$sshKeyGen.UseShellExecute = $true
$sshKeyGen.RedirectStandardOutput = $false
$sshKeyGen.RedirectStandardError = $false

$process = [System.Diagnostics.Process]::Start($sshKeyGen)
$process.WaitForExit()

if ($process.ExitCode -eq 1) {
    Write-Host "SSH key generation succeeded."
} else {
    Write-Host "SSH key generation failed. Terminating..."
    exit(-1)
}

docker ps | out-null
if (-not ($LASTEXITCODE -eq 0)){
    Write-Host "Docker is not running. Terminating..." 
    exit(-1)
}

docker compose down
docker compose up -d

# python setup script retry-launching

do {
    try {
        # Start the Python script
        & python script.py
        
        # If the script returns 0, exit the loop
        if ($LASTEXITCODE -eq 0) {
            break
        }
        else {
            # If the script returns a non-zero exit code, log the error and restart
            Write-Host "Script failed, restarting..."
        }
    }
    catch {
        # If there was an error starting the script, log the error and restart
        Write-Host "Error running Python script: $_"
    }
    
    # Wait for 5 seconds before restarting the script
    Start-Sleep -Seconds 5
} while ($true)


