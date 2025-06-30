#!/bin/bash
set -e

# Load environment variables from .env
export $(grep -v '^#' /app/.env | xargs)

# Fetch all nightlines
response=$(curl -s http://localhost:5000/public/all)

# Extract nightline_name using jq
nightlines=$(echo "$response" | jq -r '.[].nightline_name')

# Loop through each nightline and reset its status
for nl in $nightlines; do
  echo "Resetting status for: $nl"
  curl -s -X DELETE http://localhost:5000/nightline/${nl}/status \
       -H "Authorization: ${ADMIN_API_KEY}" \
       -w "\nStatus reset response for $nl: %{http_code}\n"
done