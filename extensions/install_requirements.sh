#!/bin/bash

EXTENSIONS_DIR="extensions"
EXT_IGNORE_FILE="$EXTENSIONS_DIR/ignore.txt"
ignore_dirs=("__pycache__" ".ds_store")
ignore_list=()
loaded_ext=()
read_ignore_list(){
    if [ -f "$EXT_IGNORE_FILE" ]; then
        echo "Checking in $EXT_IGNORE_FILE which extensions should be ignored..."
        while IFS= read -r line || [[ -n "$line" ]]; do
            ignore_list+=("$line")
        done < "$EXT_IGNORE_FILE"
        echo "Following extensions are ignored:"
        for ext in "${ignore_list[@]}"; do
            echo "$ext"
        done
    else
        echo "$EXT_IGNORE_FILE does not exist. Skipping ignore list."
    fi
}

should_ignore_extension(){
    local extension="$1"
    for ignored_dir in "${ignore_dirs[@]}"; do
            if [[ "$extension" == "$ignored_dir" ]]; then
            return 0
        fi
    done
    for ignored_extension in "${ignore_list[@]}"; do
        if [[ "$extension" == "$ignored_extension" ]]; then
            echo "Extensions $extension is ingored!"
            return 0
        fi
    done
    return 1
}
echo "$ingore_list"
install_requirements() {
    for extension_dir in "$EXTENSIONS_DIR"/*/; do
        ext_name=$(basename "$extension_dir")

        should_ignore_extension "$ext_name" && continue

        echo "Loading extensions: $ext_name"
        requirements_file="$extension_dir/requirements.txt"
        if [[ -f "$requirements_file" ]]; then
            echo "Installing the following requirements for the extension $ext_name:"
            cat "$requirements_file"
            echo ""
            python3 -m pip install -r "$requirements_file" | grep -v "Requirement already satisfied" || true
        else
            echo "No requirements file found for extension $ext_name. Skipping installation."
        fi
        loaded_ext+=("$ext_name")
    done
}

# Check which extensions are ignored.
read_ignore_list
