$ErrorActionPreference = "Stop"

# Use local SQLite databases for local run if no external PostgreSQL is provided
$root = $PSScriptRoot
if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL_SCHEDULER = "sqlite:///$($root.Replace('\', '/'))/test_scheduler.db"
    $env:DATABASE_URL_COURSE = "sqlite:///$($root.Replace('\', '/'))/test_course.db"
    $env:DATABASE_URL_STUDENT = "sqlite:///$($root.Replace('\', '/'))/test_student.db"
}

Write-Host "Starting Course API (Port 8001)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\courseapi'; `$env:DATABASE_URL='$($env:DATABASE_URL_COURSE)'; py -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload"

Write-Host "Starting Student API (Port 8002)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\studentapi'; `$env:DATABASE_URL='$($env:DATABASE_URL_STUDENT)'; py -m uvicorn src.main:app --host 127.0.0.1 --port 8002 --reload"

Write-Host "Starting AI Assistant API (Port 8003)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\ai-assistant-api'; py -m uvicorn src.main:app --host 127.0.0.1 --port 8003 --reload"

Write-Host "Starting Scheduler API (Port 8000)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\schedulerapi'; `$env:DATABASE_URL='$($env:DATABASE_URL_SCHEDULER)'; py -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "Starting Frontend Server (Port 5500)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npx -y serve -l tcp://127.0.0.1:5500 --no-port-switching ."

Write-Host "All services started! Opening frontend..."
Start-Sleep -Seconds 4
Start-Process "http://127.0.0.1:5500"

