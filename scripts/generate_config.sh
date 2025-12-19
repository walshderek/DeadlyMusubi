#!/bin/bash
# Generate Wan 2.2 Training Configuration
# Usage: ./generate_config.sh <project_name> [trigger_word]

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <project_name> [trigger_word]"
    echo "Example: $0 my_character ohwx"
    exit 1
fi

PROJECT_NAME="$1"
TRIGGER_WORD="${2:-ohwx}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="${SCRIPT_DIR}/../templates"
OUTPUT_DIR="${SCRIPT_DIR}/../configs"
WSL_MODEL_ROOT="/mnt/c/AI/models"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Generate TOML config
TOML_OUTPUT="${OUTPUT_DIR}/${PROJECT_NAME}.toml"
cp "${TEMPLATES_DIR}/dataset_config_template.toml" "${TOML_OUTPUT}"

# Replace placeholders
sed -i "s|\[PROJECT_NAME\]|${PROJECT_NAME}|g" "${TOML_OUTPUT}"
sed -i "s|\[TRIGGER_WORD\]|${TRIGGER_WORD}|g" "${TOML_OUTPUT}"

echo "✅ Generated TOML config: ${TOML_OUTPUT}"

# Generate training script
TRAIN_OUTPUT="${OUTPUT_DIR}/${PROJECT_NAME}_train.sh"
cp "${TEMPLATES_DIR}/wan_train_template.sh" "${TRAIN_OUTPUT}"
chmod +x "${TRAIN_OUTPUT}"

# Update project name in script
sed -i "s|PROJECT_NAME=\"\${1:-my_project}\"|PROJECT_NAME=\"${PROJECT_NAME}\"|g" "${TRAIN_OUTPUT}"
sed -i "s|TRIGGER_WORD=\"ohwx\"|TRIGGER_WORD=\"${TRIGGER_WORD}\"|g" "${TRAIN_OUTPUT}"

echo "✅ Generated training script: ${TRAIN_OUTPUT}"
echo ""
echo "Next steps:"
echo "1. Place your training images in: /mnt/c/AI/training_data/${PROJECT_NAME}/images"
echo "2. Create .txt caption files for each image"
echo "3. Run: ${TRAIN_OUTPUT}"
