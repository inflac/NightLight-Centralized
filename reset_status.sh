#!/bin/bash

# Load environment variables
export $(grep -v '^#' /app/.env | xargs)

# Get all nightline names from public API
response=$(curl -s http://localhost:5000/public/all)

# Extrahiere alle "nightline_name"-Werte
nightlines=$(echo "$response" | grep -o '"nightline_name":[^,}]*' | cut -d':' -f2 | tr -d ' "')

# Schleife über alle nightlines und sende DELETE-Request
for nl in $nightlines; do
    echo "Resetting status for: $nl"
    curl -s -X DELETE "http://localhost:5000/nightline/${nl}/status" \
         -H "Authorization: ${ADMIN_API_KEY}"
    echo -e "\n---"
done