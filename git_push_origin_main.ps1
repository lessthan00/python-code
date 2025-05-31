<#
.SYNOPSIS
    Executes git commands in all immediate subdirectories (non-recursive).
.DESCRIPTION
    Processes each immediate child directory by running:
    - git add .
    - git commit -m "update"
    - git push origin main
#>

# 主脚本开始
$subDirs = Get-ChildItem -Directory

# 遍历每个子目录
foreach ($dir in $subDirs) {
    $currentPath = Get-Location
    
    try {
        # 显示当前处理目录
        Write-Host "Processing: $($dir.FullName)" -ForegroundColor Yellow
        
        Set-Location -Path $dir.FullName
        
        # 执行git三步操作
        git add .
        git commit -m "update"
        git push -u origin main
        
        Write-Host "Completed: $($dir.Name)" -ForegroundColor Green
    }
    catch {
        # 错误处理
        Write-Host "Error in $($dir.Name): $_" -ForegroundColor Red
    }
    finally {
        # 确保返回原目录
        Set-Location -Path $currentPath
    }
}

# 结束提示
Write-Host "All directories processed." -ForegroundColor Cyan