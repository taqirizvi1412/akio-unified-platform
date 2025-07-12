# test-api.ps1
Write-Host "Testing HubSpot API Integration..." -ForegroundColor Cyan

# Test connection
Write-Host "`nTesting connection..." -ForegroundColor Yellow
$connection = Invoke-RestMethod -Uri "http://localhost:3000/api/hubspot/test-connection" -Method Get
Write-Host "Connection Status: $($connection.connected)" -ForegroundColor Green
Write-Host "Region: $($connection.region)" -ForegroundColor Green

# Test creating a contact
Write-Host "`nCreating test contact..." -ForegroundColor Yellow
$body = @{
    email = "powershell-test@example.com"
    firstname = "PowerShell"
    lastname = "Test"
    phone = "+1112223333"
} | ConvertTo-Json

try {
    $contact = Invoke-RestMethod -Uri "http://localhost:3000/api/hubspot/contacts" -Method Post -Body $body -ContentType "application/json"
    Write-Host "Contact created/updated successfully!" -ForegroundColor Green
    Write-Host "Contact ID: $($contact.contact.id)" -ForegroundColor Green
    Write-Host "Action: $($contact.action)" -ForegroundColor Green
} catch {
    Write-Host "Error creating contact: $_" -ForegroundColor Red
}

# Get stats
Write-Host "`nFetching statistics..." -ForegroundColor Yellow
$stats = Invoke-RestMethod -Uri "http://localhost:3000/api/hubspot/stats" -Method Get
Write-Host "Total Contacts: $($stats.totalContacts)" -ForegroundColor Green
Write-Host "Total Calls: $($stats.totalCalls)" -ForegroundColor Green