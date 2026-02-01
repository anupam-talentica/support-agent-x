#!/bin/bash

echo "Validating Terraform syntax across all components..."

components=(
    "security_group"
    "iam"
    "s3_bucket"
    "rds"
    "ec2"
    "alb"
    "ecr"
    "cloudfront"
)

FAILED_COMPONENTS=()

for component in "${components[@]}"; do
    echo ""
    echo "🔍 Validating $component..."
    cd "components/$component" || {
        echo "❌ Directory not found: $component"
        FAILED_COMPONENTS+=("$component")
        continue
    }

    # Init without touching backend
    terraform init -backend=false -input=false -no-color >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "❌ terraform init failed for $component"
        FAILED_COMPONENTS+=("$component")
        cd ../..
        continue
    fi

    # Validate
    terraform validate -no-color
    if [ $? -ne 0 ]; then
        echo "❌ terraform validate failed for $component"
        FAILED_COMPONENTS+=("$component")
        cd ../..
        continue
    fi

    # Format check
    terraform fmt -check -recursive -no-color
    if [ $? -ne 0 ]; then
        echo "⚠️ Formatting issues in $component"
        FAILED_COMPONENTS+=("$component")
    else
        echo "✅ $component passed"
    fi

    cd ../..
done

echo ""
echo "=============================="
if [ ${#FAILED_COMPONENTS[@]} -eq 0 ]; then
    echo "🎉 All Terraform components validated successfully!"
    exit 0
else
    echo "❌ Validation failed for the following components:"
    for c in "${FAILED_COMPONENTS[@]}"; do
        echo "   - $c"
    done
    exit 1
fi

