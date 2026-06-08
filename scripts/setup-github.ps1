# Configurar GitHub e publicar DUNNAA
#
# Pré-requisito: GitHub CLI instalado (winget install GitHub.cli)
#
# Uso:
#   cd d:\dunna
#   .\scripts\setup-github.ps1
#   .\scripts\setup-github.ps1 -Owner seu-usuario -Private

param(
    [string]$Owner = "innexar-plat",
    [string]$RepoName = "dunnaa",
    [switch]$Private = $true,
    [switch]$SkipPush,
    [switch]$UseHttps
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) não encontrado. Instale: winget install GitHub.cli"
}

Write-Host "=== 1/4 Login GitHub ===" -ForegroundColor Cyan
gh auth status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "gh não autenticado. Para criar o repo via CLI:" -ForegroundColor Yellow
    Write-Host "  gh auth login --git-protocol ssh --skip-ssh-key -w" -ForegroundColor Yellow
    Write-Host "Ou crie manualmente: https://github.com/new?name=$RepoName" -ForegroundColor Yellow
}

if (-not $Owner) {
    $Owner = (gh api user -q .login)
    Write-Host "Usuário detectado: $Owner" -ForegroundColor Green
}

$remoteUrl = if ($UseHttps) {
    "https://github.com/$Owner/$RepoName.git"
} else {
    "git@github.com:${Owner}/${RepoName}.git"
}

Write-Host "`n=== 2/4 Criar repositório $Owner/$RepoName ===" -ForegroundColor Cyan
$visibility = if ($Private) { "--private" } else { "--public" }

gh repo view "$Owner/$RepoName" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Repositório já existe." -ForegroundColor Yellow
} else {
    gh repo create $RepoName $visibility --description "DUNNAA - agendamento e assinaturas para barbearias" --confirm
}

Write-Host "`n=== 3/4 Configurar remote ===" -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin $remoteUrl
git remote -v

if (-not $SkipPush) {
    Write-Host "`n=== 4/4 Push ===" -ForegroundColor Cyan
    git push -u origin master
    if ($LASTEXITCODE -ne 0) {
        git push -u origin main 2>$null
    }
}

Write-Host "`nPronto: https://github.com/$Owner/$RepoName" -ForegroundColor Green
