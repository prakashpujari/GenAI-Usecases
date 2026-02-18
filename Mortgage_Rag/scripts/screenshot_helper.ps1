# Screenshot Helper Script for SecureMortgageAI Documentation
# This script helps organize and prepare screenshots for documentation

Write-Host "📸 SecureMortgageAI Screenshot Helper" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Create directory structure
$screenshotDir = "screenshots"
$subdirs = @("raw", "annotated", "comparisons", "presentations", "videos")

Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow

if (!(Test-Path $screenshotDir)) {
    New-Item -ItemType Directory -Path $screenshotDir | Out-Null
    Write-Host "✅ Created $screenshotDir/" -ForegroundColor Green
}

foreach ($dir in $subdirs) {
    $path = Join-Path $screenshotDir $dir
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
        Write-Host "✅ Created $screenshotDir/$dir/" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "📋 Screenshot Checklist:" -ForegroundColor Cyan
Write-Host ""

# Define screenshot checklist
$screenshots = @(
    @{Num=1; Name="01_landing_page.png"; Desc="Landing page with empty state"},
    @{Num=2; Name="02_file_upload_dialog.png"; Desc="Windows file picker dialog"},
    @{Num=3; Name="03_processing_embeddings.png"; Desc="Processing spinner"},
    @{Num=4; Name="04_upload_success.png"; Desc="Upload complete with stats table"},
    @{Num=5; Name="05_pii_detection_expanded.png"; Desc="PII detection table expanded"},
    @{Num=6; Name="06_security_guardrails_sidebar.png"; Desc="Security features list"},
    @{Num=7; Name="07_document_statistics.png"; Desc="Document stats close-up"},
    @{Num=8; Name="08_query_income.png"; Desc="First query - income question"},
    @{Num=9; Name="09_response_with_sources.png"; Desc="AI response with sources"},
    @{Num=10; Name="10_followup_employment.png"; Desc="Follow-up employment query"},
    @{Num=11; Name="11_ssn_redaction_demo.png"; Desc="SSN query showing redaction"},
    @{Num=12; Name="12_blocked_prompt_injection.png"; Desc="Blocked prompt injection"},
    @{Num=13; Name="13_blocked_inappropriate.png"; Desc="Blocked inappropriate content"},
    @{Num=14; Name="14_warning_offtopic.png"; Desc="Warning for off-topic query"},
    @{Num=15; Name="15_full_conversation.png"; Desc="Full conversation thread"},
    @{Num=16; Name="16_relevance_scores.png"; Desc="Source relevance comparison"},
    @{Num=17; Name="17_clear_chat_action.png"; Desc="Clear chat history button"}
)

# Display checklist
foreach ($shot in $screenshots) {
    $status = "[ ]"
    $path = Join-Path $screenshotDir "raw" $shot.Name
    if (Test-Path $path) {
        $status = "[✓]"
        Write-Host "$status #$($shot.Num): $($shot.Desc)" -ForegroundColor Green
    } else {
        Write-Host "$status #$($shot.Num): $($shot.Desc)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📊 Progress:" -ForegroundColor Cyan

# Count completed screenshots
$completed = 0
foreach ($shot in $screenshots) {
    $path = Join-Path $screenshotDir "raw" $shot.Name
    if (Test-Path $path) {
        $completed++
    }
}

$total = $screenshots.Count
$percentage = [math]::Round(($completed / $total) * 100)

Write-Host "$completed / $total screenshots captured ($percentage percent)" -ForegroundColor Yellow

if ($completed -eq $total) {
    Write-Host "🎉 All screenshots captured! Great job!" -ForegroundColor Green
}

Write-Host ""
Write-Host "💡 Quick Actions:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the app:" -ForegroundColor White
Write-Host "   streamlit run app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Capture screenshot:" -ForegroundColor White
Write-Host "   Press Win + Shift + S, then select area" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Open screenshots folder:" -ForegroundColor White
Write-Host "   explorer screenshots\raw" -ForegroundColor Gray
Write-Host ""
Write-Host "4. View guide:" -ForegroundColor White
Write-Host "   code SCREENSHOT_GUIDE.md" -ForegroundColor Gray
Write-Host ""

# Offer to open screenshots folder
Write-Host "📂 Open screenshots folder now? (Y/N): " -ForegroundColor Yellow -NoNewline
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    explorer (Join-Path $screenshotDir "raw")
    Write-Host "✅ Opened screenshots/raw/" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Launch app: streamlit run app.py" -ForegroundColor White
Write-Host "2. Follow SCREENSHOT_GUIDE.md for capture instructions" -ForegroundColor White
Write-Host "3. Save screenshots to screenshots/raw/ folder" -ForegroundColor White
Write-Host "4. Run this script again to check progress" -ForegroundColor White
Write-Host ""
Write-Host "Good luck! 📸" -ForegroundColor Green
