# Function to retry npm commands
function Invoke-NpmCommandWithRetry {
    param(
        [string]$Command,
        [int]$MaxAttempts = 3,
        [int]$DelaySeconds = 5
    )
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        Write-Host "Attempt $i of $MaxAttempts - Running: $Command"
        
        # Execute the command
        $result = Invoke-Expression $Command
        
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        
        Write-Host "Attempt $i failed. Waiting $DelaySeconds seconds before retry..."
        Start-Sleep -Seconds $DelaySeconds
    }
    
    return $false
}

# Configure npm settings
Write-Host "Configuring npm settings..."
npm config set strict-ssl false
npm config set registry "http://registry.npmjs.org/"
npm config delete proxy
npm config delete https-proxy

# Clean up node_modules if it exists
if (Test-Path node_modules) {
    Write-Host "Cleaning up existing node_modules..."
    # Kill any processes that might be locking files
    taskkill /F /IM node.exe 2>$null
    Start-Sleep -Seconds 2
    Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Clean up package-lock.json if it exists
if (Test-Path package-lock.json) {
    Write-Host "Removing package-lock.json..."
    Remove-Item package-lock.json -ErrorAction SilentlyContinue
}

# Clear npm cache
Write-Host "Clearing npm cache..."
npm cache clean --force

# Create a temporary package.json with minimal dependencies first
$tempPackageJson = @{
    name = "kifiya-mini-agent-platform-frontend"
    version = "0.1.0"
    private = $true
    dependencies = @{
        "react" = "^18.2.0"
        "react-dom" = "^18.2.0"
        "react-scripts" = "5.0.1"
    }
}

Write-Host "Creating temporary package.json..."
$tempPackageJson | ConvertTo-Json -Depth 10 | Set-Content -Path "package.json"

# Install base dependencies first
Write-Host "Installing base dependencies..."
if (-not (Invoke-NpmCommandWithRetry "npm install --legacy-peer-deps")) {
    Write-Host "Failed to install base dependencies. Please check your network connection and try again."
    exit 1
}

# Now update package.json with all dependencies
$fullPackageJson = @{
    name = "kifiya-mini-agent-platform-frontend"
    version = "0.1.0"
    private = $true
    dependencies = @{
        "@emotion/react" = "^11.11.3"
        "@emotion/styled" = "^11.11.0"
        "@mui/material" = "^5.15.10"
        "@mui/icons-material" = "^5.15.10"
        "@reduxjs/toolkit" = "^2.2.1"
        "axios" = "^1.6.7"
        "formik" = "^2.4.5"
        "react" = "^18.2.0"
        "react-dom" = "^18.2.0"
        "react-redux" = "^9.1.0"
        "react-router-dom" = "^6.22.0"
        "react-scripts" = "5.0.1"
        "react-toastify" = "^10.0.4"
        "web-vitals" = "^2.1.4"
        "yup" = "^1.3.3"
    }
    devDependencies = @{
        "@types/jest" = "^27.5.2"
        "@types/node" = "^16.18.80"
        "@types/react" = "^18.2.55"
        "@types/react-dom" = "^18.2.19"
        "typescript" = "^4.9.5"
    }
    scripts = @{
        start = "react-scripts start"
        build = "react-scripts build"
        test = "react-scripts test"
        eject = "react-scripts eject"
    }
    eslintConfig = @{
        extends = @("react-app", "react-app/jest")
    }
    browserslist = @{
        production = @(">0.2%", "not dead", "not op_mini all")
        development = @("last 1 chrome version", "last 1 firefox version", "last 1 safari version")
    }
}

Write-Host "Updating package.json with all dependencies..."
$fullPackageJson | ConvertTo-Json -Depth 10 | Set-Content -Path "package.json"

# Install remaining dependencies
Write-Host "Installing remaining dependencies..."
if (-not (Invoke-NpmCommandWithRetry "npm install --legacy-peer-deps")) {
    Write-Host "Failed to install remaining dependencies. Please check your network connection and try again."
    exit 1
}

# Create TypeScript configuration if it doesn't exist
if (-not (Test-Path tsconfig.json)) {
    Write-Host "Creating TypeScript configuration..."
    $tsConfig = @{
        compilerOptions = @{
            target = "es5"
            lib = @("dom", "dom.iterable", "esnext")
            allowJs = $true
            skipLibCheck = $true
            esModuleInterop = $true
            allowSyntheticDefaultImports = $true
            strict = $true
            forceConsistentCasingInFileNames = $true
            noFallthroughCasesInSwitch = $true
            module = "esnext"
            moduleResolution = "node"
            resolveJsonModule = $true
            isolatedModules = $true
            noEmit = $true
            jsx = "react-jsx"
        }
        include = @("src")
    }
    $tsConfig | ConvertTo-Json -Depth 10 | Set-Content -Path "tsconfig.json"
}

Write-Host "Setup complete. Starting development server..."
Write-Host "If you encounter any issues, try running 'npm start' manually."

# Try to start the development server
if (-not (Invoke-NpmCommandWithRetry "npm start")) {
    Write-Host "Failed to start the development server. Please try running 'npm start' manually."
} 