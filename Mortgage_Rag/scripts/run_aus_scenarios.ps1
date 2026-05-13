$ErrorActionPreference = "Stop"

$baseUrl = "http://localhost:8000"
$headers = @{ "Content-Type" = "application/json" }

function Invoke-AusScenario {
    param(
        [string]$Name,
        [hashtable]$Payload
    )

    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    $json = $Payload | ConvertTo-Json -Depth 4
    $response = Invoke-RestMethod -Method Post -Uri "$baseUrl/aus/evaluate" -Headers $headers -Body $json
    Write-Host "finding: $($response.finding)" -ForegroundColor Green
    Write-Host "reasons:" -ForegroundColor Yellow
    foreach ($reason in $response.reasons) {
        Write-Host "- $reason"
    }
    Write-Host "required_documents_count: $($response.required_documents.Count)"
}

Write-Host "Checking health endpoint..." -ForegroundColor Cyan
$health = Invoke-RestMethod -Method Get -Uri "$baseUrl/health"
Write-Host "health: $($health.status)" -ForegroundColor Green

$approvePayload = @{
    credit_score = 742
    dti = 29.5
    ltv = 75.0
    income = 120000
    loan_amount = 420000
    property_value = 560000
    loan_type = "Conventional"
    reserves = 6
    occupancy_type = "Primary"
}

$referEligiblePayload = @{
    credit_score = 742
    dti = 44.0
    ltv = 75.0
    income = 120000
    loan_amount = 420000
    property_value = 560000
    loan_type = "Conventional"
    reserves = 6
    occupancy_type = "Primary"
}

$referIneligiblePayload = @{
    credit_score = 600
    dti = 29.5
    ltv = 75.0
    income = 120000
    loan_amount = 420000
    property_value = 560000
    loan_type = "Conventional"
    reserves = 6
    occupancy_type = "Primary"
}

Invoke-AusScenario -Name "Approve/Eligible" -Payload $approvePayload
Invoke-AusScenario -Name "Refer/Eligible" -Payload $referEligiblePayload
Invoke-AusScenario -Name "Refer/Ineligible" -Payload $referIneligiblePayload

Write-Host "`nAll scenarios completed." -ForegroundColor Cyan
