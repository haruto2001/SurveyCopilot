#!/bin/bash

cd tools/acl-anthology
echo "Updating 'acl-anthology' repository to the latest version..."
if git pull; then
    echo "Repository successfully updated."
else
    echo "Failed to update the repository."
    exit 1
fi

cd /work
exec "$@"