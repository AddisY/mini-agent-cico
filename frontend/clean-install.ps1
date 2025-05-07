# Stop on first error
$ErrorActionPreference = "Stop"

Write-Host "Cleaning up existing installation..."
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
}
if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json"
}

Write-Host "Setting npm configurations..."
npm config set registry "https://registry.npmjs.org/"
npm config set strict-ssl true

Write-Host "Installing dependencies..."
npm install --legacy-peer-deps

Write-Host "Starting development server..."
npm start 