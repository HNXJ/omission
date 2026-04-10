# Local-only
# This script is for local development and contains machine-specific paths and configurations.

$ErrorActionPreference = "Continue"

$Workspace = "D:\Analysis\Omission\local-workspace"
$PipelineScript = "$Workspace\codes\scriptsun_predictive_routing_pipeline.py"
$LogFile = "$Workspace\predictive_routing_pipeline.log"

Write-Output "======================================================" | Out-File -FilePath $LogFile -Append
Write-Output "Starting Offline Headless Execution of Predictive Routing Pipeline" | Out-File -FilePath $LogFile -Append
Write-Output "Time: $(Get-Date)" | Out-File -FilePath $LogFile -Append
Write-Output "======================================================" | Out-File -FilePath $LogFile -Append

try {
    # Activate virtual environment if necessary here
    # e.g., & "C:\path	o\venv\Scripts\Activate.ps1"
    
    Write-Output "Executing python pipeline..." | Out-File -FilePath $LogFile -Append
    python $PipelineScript 2>&1 | Out-File -FilePath $LogFile -Append
    
    Write-Output "Pipeline execution finished with Exit Code: $LASTEXITCODE" | Out-File -FilePath $LogFile -Append
}
catch {
    Write-Output "CRITICAL FAILURE in Pipeline Execution: $_" | Out-File -FilePath $LogFile -Append
}

Write-Output "======================================================" | Out-File -FilePath $LogFile -Append
Write-Output "Pipeline Completed at $(Get-Date)" | Out-File -FilePath $LogFile -Append
Write-Output "======================================================" | Out-File -FilePath $LogFile -Append
