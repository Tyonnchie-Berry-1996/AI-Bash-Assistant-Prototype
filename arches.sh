#!/bin/bash

TARGET_INFO=$(koji list-targets --name="$NAME")
BUILD_TAG=$(printf '%s\n' "$TARGET_INFO" | awk 'NR > 2 && NF >= 3 {print $2; exit}')

if [ -z "$BUILD_TAG" ]; then
    echo "KERNEL_ARCH_COUNT=0"
    echo "KERNEL_ARCH_ERROR=No build tag found for target: $NAME"
    exit 1
fi

ARCHES_LINE=$(koji taginfo "$BUILD_TAG" | grep -i "Arches:")

ARCHES=$(printf '%s\n' "$ARCHES_LINE" | sed -E 's/^[[:space:]]*Arches:[[:space:]]*//I')

if [ -z "$ARCHES" ]; then
    echo "KERNEL_ARCH_COUNT=0"
    echo "KERNEL_ARCH_ERROR=No arches found for build tag: $BUILD_TAG"
    exit 1
fi

count=0

for arch in $ARCHES; do
    count=$((count + 1))
    echo "$arch"
done
