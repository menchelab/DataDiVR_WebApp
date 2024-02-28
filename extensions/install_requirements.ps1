$EXTENSIONS_DIR = "extensions"
$EXT_IGNORE_FILE = "$EXTENSIONS_DIR\ignore.txt"
$ignore_dirs = @("__pycache__", ".ds_store")
$ignore_list = @()
$loaded_ext = @()

function Read-IgnoreList {
    if (Test-Path $EXT_IGNORE_FILE -PathType Leaf) {
        Write-Host "Checking in $EXT_IGNORE_FILE which extensions should be ignored..."
        $ignore_list = Get-Content $EXT_IGNORE_FILE
        Write-Host "Following extensions are ignored:"
        foreach ($ext in $ignore_list) {
            Write-Host $ext
        }
    }
    else {
        Write-Host "$EXT_IGNORE_FILE does not exist. Skipping ignore list."
    }
}

function Should-IgnoreExtension {
    param($extension)
    foreach ($ignored_dir in $ignore_dirs) {
        if ($extension -eq $ignored_dir) {
            Write-Host "Extensions $extension is ignored!"
            return $true
        }
    }
    foreach ($ignored_extension in $ignore_list) {
        if ($extension -eq $ignored_extension) {
            Write-Host "Extensions $extension is ignored!"
            return $true
        }
    }
    return $false
}

function Install-Requirements {
    foreach ($extension_dir in Get-ChildItem "$EXTENSIONS_DIR\*" -Directory) {
        $ext_name = $extension_dir.Name

        if (Should-IgnoreExtension $ext_name) { continue }

        Write-Host "Loading extensions: $ext_name"
        $requirements_file = "$extension_dir\requirements.txt"
        if (Test-Path $requirements_file -PathType Leaf) {
            Write-Host "Installing the following requirements for the extension $ext_name\:"
            Get-Content $requirements_file
            Write-Host ""
            python -m pip install -r $requirements_file
        } else {
            Write-Host "No requirements file found for extension $ext_name. Skipping installation."
        }
        $loaded_ext += $ext_name
    }
    Write-Host "Finished installing all requirements for the following extensions:"
    foreach ($ext in $loaded_ext) {
        Write-Host $ext
    }
}

# Check if the ignore file exists, then read it
Read-IgnoreList
