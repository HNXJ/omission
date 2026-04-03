$ErrorActionPreference = "Stop"
$Workspace = "D:\Analysis\Omission\local-workspace"
$ScriptsDir = "$Workspace\codes\scripts"
$LogFile = "$Workspace\session_progress.log"

function Run-Script {
    param([string]$ScriptName)
    $ScriptPath = Join-Path $ScriptsDir $ScriptName
    if (Test-Path $ScriptPath) {
        Write-Output "[$(Get-Date -Format 'HH:mm:ss')] Starting: $ScriptName" | Out-File -FilePath $LogFile -Append
        python $ScriptPath
        if ($LASTEXITCODE -eq 0) {
            Write-Output "[$(Get-Date -Format 'HH:mm:ss')] SUCCESS: $ScriptName" | Out-File -FilePath $LogFile -Append
        } else {
            Write-Output "[$(Get-Date -Format 'HH:mm:ss')] FAILED ($LASTEXITCODE): $ScriptName" | Out-File -FilePath $LogFile -Append
        }
    } else {
        Write-Output "[$(Get-Date -Format 'HH:mm:ss')] MISSING: $ScriptName" | Out-File -FilePath $LogFile -Append
    }
}

Write-Output "--- Starting OMISSION 2026 Pipeline ---" | Out-File -FilePath $LogFile

Run-Script "generate_fig02_eye_dva.py"
Run-Script "generate_fig03_spk_avg.py"
Run-Script "generate_fig04_kmeans.py"
Run-Script "generate_fig05_06_lfp_tfr.py"
Run-Script "generate_fig07_lfp_spk_corr.py"
Run-Script "generate_fig08_omission_effect.py"

Write-Output "[$(Get-Date -Format 'HH:mm:ss')] Starting Vision Audit..." | Out-File -FilePath $LogFile -Append
Run-Script "vision_audit.py"

Write-Output "--- Pipeline Complete ---" | Out-File -FilePath $LogFile -Append
