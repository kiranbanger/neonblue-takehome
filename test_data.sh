#!/bin/bash

# Script to test the events POST endpoint with random data
# Requires: curl, jq

BASE_URL="http://localhost:5000"
TOKEN="test-token-123"

# Arrays for random selection
EVENT_TYPES=("click" "purchase" "signup")

# Function to generate random properties JSON
generate_properties() {
    local rand=$((RANDOM % 3))
    case $rand in
        0)
            echo '{"page":"home","duration":'$((RANDOM % 60))'}'
            ;;
        1)
            echo '{"product_id":'$((RANDOM % 1000))',"amount":'$((RANDOM % 500))'}'
            ;;
        2)
            echo '{"source":"organic","device":"mobile"}'
            ;;
    esac
}

# Function to make a curl request
make_request() {
    local user_id=$2
    local event_type=${EVENT_TYPES[$((RANDOM % 3))]}
    local properties=$(generate_properties)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.000000Z")

    echo "Request $1:"
    echo "  User ID: $user_id"
    echo "  Event Type: $event_type"
    echo "  Timestamp: $timestamp"
    echo "  Properties: $properties"
    echo ""

    # Create JSON payload
    local payload=$(cat <<EOF
{
  "user_id": "$user_id",
  "type": "$event_type",
  "timestamp": "$timestamp",
  "properties": $properties
}
EOF
)

    # Make the request
    curl -X POST "$BASE_URL/events/" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        -w "\nHTTP Status: %{http_code}\n" \
        -s

    echo ""
    echo "---"
    echo ""
}

# Function to get assignment
get_assignment() {
    local experiment_id=$1
    local user_id=$2

    echo "Getting assignment for:"
    echo "  Experiment ID: $experiment_id"
    echo "  User ID: $user_id"
    echo ""

    RESPONSE=$(curl -X GET "$BASE_URL/experiments/$experiment_id/assignment/$user_id" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -w "\n%{http_code}" \
        -s)

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    echo "Response: $BODY"
    echo "HTTP Status: $HTTP_CODE"
    echo ""

    if [ "$HTTP_CODE" != "200" ]; then
        echo "ERROR: Got HTTP $HTTP_CODE for experiment_id=$experiment_id, user_id=$user_id"
    fi

    echo "---"
    echo ""
}

# Create an experiment first
echo "=== CREATING EXPERIMENT ==="
echo ""

EXPERIMENT_PAYLOAD=$(cat <<EOF
{
  "name": "Test Experiment7",
  "description": "Test experiment for assignment endpoint",
  "variants": [
    {"name": "control7", "traffic_allocation": 25},
    {"name": "treatment7a", "traffic_allocation": 25},
    {"name": "treatment7b", "traffic_allocation": 25},
    {"name": "treatment7c", "traffic_allocation": 25}
  ]
}
EOF
)

EXPERIMENT_RESPONSE=$(curl -X POST "$BASE_URL/experiments/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$EXPERIMENT_PAYLOAD" \
    -s)

echo "Experiment Response: $EXPERIMENT_RESPONSE"
echo ""

# Extract experiment ID using jq if available, otherwise use grep
if command -v jq &> /dev/null; then
    EXPERIMENT_ID=$(echo "$EXPERIMENT_RESPONSE" | jq -r '.id' 2>/dev/null)
else
    EXPERIMENT_ID=$(echo "$EXPERIMENT_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
fi

if [ -z "$EXPERIMENT_ID" ] || [ "$EXPERIMENT_ID" = "null" ]; then
    echo "Failed to create experiment"
    echo "Full response: $EXPERIMENT_RESPONSE"
    exit 1
fi

echo "Created experiment with ID: $EXPERIMENT_ID"
echo ""

# Get assignments for 10 users, then post 5 events per user
echo "=== GETTING ASSIGNMENTS AND POSTING EVENTS ==="
echo ""

for i in {1..1000}; do
    user_id="user_$(openssl rand -hex 8)"

    echo "User $i: $user_id"
    echo ""

    # Get assignment first
    echo "1. Getting assignment..."
    get_assignment "$EXPERIMENT_ID" "$user_id"

    # Then post 5 events for this user
    echo "2. Posting 5 events for this user..."
    for j in {1..2}; do
        echo "   Event $j/2"
        make_request "$i-$j" "$user_id"
        sleep 0.3
    done

    echo ""
    sleep 1
done

echo "All 1000 users with 2 events each completed! (2000 total events)"

