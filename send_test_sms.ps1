# Test SMS Sender Script for Demo
# This simulates receiving an SMS from a citizen

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "    SMS Livelihood Helpline - Test SMS Sender" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Predefined test messages
$testMessages = @(
    @{
        name = "Employment Query";
        phone = "+919876543220";
        text = "I need help finding a job in construction work"
    };
    @{
        name = "Training Program";
        phone = "+919876543221";
        text = "Are there any skill training programs available in my area?"
    };
    @{
        name = "Government Scheme";
        phone = "+919876543222";
        text = "I want to know about government schemes for small business"
    };
    @{
        name = "Loan Assistance";
        phone = "+919876543223";
        text = "I need agricultural loan for purchasing equipment"
    };
    @{
        name = "General Help";
        phone = "+919876543224";
        text = "Please help me with livelihood support options"
    }
)

# Display menu
Write-Host "Select a test message to send:" -ForegroundColor Yellow
Write-Host ""
for ($i = 0; $i -lt $testMessages.Count; $i++) {
    Write-Host "  [$($i+1)] $($testMessages[$i].name)" -ForegroundColor White
    Write-Host "      From: $($testMessages[$i].phone)" -ForegroundColor Gray
    Write-Host "      Message: $($testMessages[$i].text)" -ForegroundColor Gray
    Write-Host ""
}
Write-Host "  [6] Custom message" -ForegroundColor White
Write-Host "  [0] Exit" -ForegroundColor Red
Write-Host ""

# Get user choice
$choice = Read-Host "Enter your choice (0-6)"

if ($choice -eq "0") {
    Write-Host "Exiting..." -ForegroundColor Yellow
    exit
}

$phone = ""
$text = ""

if ($choice -eq "6") {
    # Custom message
    Write-Host ""
    $phone = Read-Host "Enter phone number (e.g., +919876543210)"
    $text = Read-Host "Enter message text"
} elseif ([int]$choice -ge 1 -and [int]$choice -le 5) {
    # Predefined message
    $selected = $testMessages[[int]$choice - 1]
    $phone = $selected.phone
    $text = $selected.text
    
    Write-Host ""
    Write-Host "Selected: $($selected.name)" -ForegroundColor Green
} else {
    Write-Host "Invalid choice!" -ForegroundColor Red
    exit
}

# Send the SMS
Write-Host ""
Write-Host "Sending SMS..." -ForegroundColor Yellow
Write-Host "  From: $phone" -ForegroundColor Cyan
Write-Host "  Message: $text" -ForegroundColor Cyan
Write-Host ""

try {
    $body = @{
        phone = $phone
        text = $text
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8080/webhook/sms" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -UseBasicParsing

    Write-Host "[OK] SMS sent successfully!" -ForegroundColor Green
    Write-Host "  Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Response:" -ForegroundColor White
    Write-Host "  $($response.Content)" -ForegroundColor Gray
    Write-Host ""
    Write-Host ">> Check your dashboard - a new ticket should appear!" -ForegroundColor Yellow
    
} catch {
    Write-Host "[ERROR] Error sending SMS:" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Make sure:" -ForegroundColor Yellow
    Write-Host "  1. Docker containers are running (docker-compose up)" -ForegroundColor Yellow
    Write-Host "  2. Backend is accessible at http://localhost:8080" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
