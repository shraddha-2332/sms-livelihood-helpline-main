# SMS Test Script for PowerShell
# Send test messages to the helpline

$API_URL = "http://localhost:8080"
$WEBHOOK_ENDPOINT = "$API_URL/webhook/sms"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " SMS Helpline Test Script" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check webhook status
Write-Host "Checking webhook status..." -ForegroundColor Cyan
try {
    $statusResponse = Invoke-RestMethod -Uri "$API_URL/webhook/status" -Method GET
    Write-Host "[OK] Webhook Status: " -NoNewline -ForegroundColor Green
    Write-Host $statusResponse.status
    Write-Host "     Queue Length: $($statusResponse.queue_length)"
    Write-Host ""
} catch {
    Write-Host "[WARNING] Could not connect to webhook" -ForegroundColor Yellow
    Write-Host "          Make sure Docker containers are running!" -ForegroundColor Yellow
    Write-Host ""
}

# Test messages
$testMessages = @(
    @{
        phone = "+919876543210"
        text = "I need help finding a job in construction work"
    },
    @{
        phone = "+919876543211"
        text = "I want to learn new skills. Are there any training programs?"
    },
    @{
        phone = "+919876543212"
        text = "I need a loan to start a small business"
    },
    @{
        phone = "+919876543213"
        text = "What government schemes are available for farmers?"
    },
    @{
        phone = "+919876543214"
        text = "I am looking for work near Mumbai"
    }
)

Write-Host "Sending test messages..." -ForegroundColor Cyan
Write-Host ""

foreach ($msg in $testMessages) {
    $body = @{
        from = $msg.phone
        text = $msg.text
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri $WEBHOOK_ENDPOINT -Method POST -Body $body -ContentType "application/json"
        
        Write-Host "[SENT] From: $($msg.phone)" -ForegroundColor Green
        $shortText = if ($msg.text.Length -gt 50) { $msg.text.Substring(0, 50) + "..." } else { $msg.text }
        Write-Host "       Message: $shortText"
        Write-Host "       Status: $($response.status)"
        Write-Host "       Message ID: $($response.message_id)"
        Write-Host "------------------------------------------------------------"
    } catch {
        Write-Host "[ERROR] Could not send message: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "        Phone: $($msg.phone)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[OK] Test complete! Check your dashboard for the new tickets." -ForegroundColor Green
Write-Host ""
Write-Host "TIP: The messages are processed by the worker in the background." -ForegroundColor Yellow
Write-Host "     It may take a few seconds for them to appear in the dashboard." -ForegroundColor Yellow
Write-Host ""
