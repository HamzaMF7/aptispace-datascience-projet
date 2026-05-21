# PowerShell Script for Automated Environment Setup on Windows using Chocolatey
$ErrorActionPreference = "Stop"

# Vérification des privilèges Administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "⚠️ Ce script doit être exécuté en tant qu'Administrateur ! Veuillez ouvrir PowerShell en mode Administrateur et réessayer."
    Exit
}

Write-Host "🚀 Démarrage de l'installation automatisée pour Windows..." -ForegroundColor Cyan

# 1. Vérification et installation de Chocolatey
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "ℹ️ Chocolatey n'est pas détecté. Installation de Chocolatey en cours..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
} else {
    Write-Host "✅ Chocolatey est déjà installé." -ForegroundColor Green
}

# Recharger les variables d'environnement dans la session actuelle
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# S'assurer que le chemin de Chocolatey est bien présent dans la session actuelle
$chocoPath = "$env:ALLUSERSPROFILE\chocolatey\bin"
if (Test-Path $chocoPath) {
    if ($env:Path -notlike "*chocolatey*") {
        $env:Path += ";$chocoPath"
    }
}

# 2. Installation des dépendances système
Write-Host "📦 Installation des outils requis..." -ForegroundColor Cyan

# Python 3.12 (ou version supérieure disponible)
Write-Host "🐍 Installation de Python 3..." -ForegroundColor Yellow
choco install python3 --version 3.12.2 -y --skip-automated-dependency-resolution

# Recharger le PATH pour inclure Python nouvellement installé
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Installation de Jupyter via pip
Write-Host "🐍 Installation de Jupyter..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install jupyter


# Quarto CLI
Write-Host "✍️ Installation de Quarto CLI..." -ForegroundColor Yellow
choco install quarto -y

# Git CLI
Write-Host "✍️ Installation de Git..." -ForegroundColor Yellow
choco install git -y

# Typst (PDF Engine ultra-rapide)
Write-Host "⚡ Installation de Typst..." -ForegroundColor Yellow
choco install typst -y

# Go-Task (Taskfile)
Write-Host "⚙️ Installation de Go-Task..." -ForegroundColor Yellow
choco install go-task -y

Write-Host "✅ Installation terminée avec succès !" -ForegroundColor Green
Write-Host "⚠️ IMPORTANT : Veuillez fermer et rouvrir votre terminal pour appliquer les changements globaux de PATH." -ForegroundColor Yellow
