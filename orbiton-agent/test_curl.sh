#!/bin/bash
# Test Z.AI API with curl

# Load environment variables
source .env

echo "======================================"
echo "Z.AI API Test with curl"
echo "======================================"
echo "API Key: ${OPENAI_API_KEY:0:20}..."
echo "Base URL: $BASE_URL"
echo "Model: $ORBITON_LLM_MODEL"
echo "======================================"

# Test 1: List available models
echo -e "\n[Test 1] Listing available models..."
echo "Endpoint: $BASE_URL/models"
echo ""

curl -s "$BASE_URL/models" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" | jq '.' || echo "Failed to parse JSON"

echo -e "\n======================================"

# Test 2: Simple chat completion
echo -e "\n[Test 2] Testing chat completion..."
echo "Endpoint: $BASE_URL/chat/completions"
echo "Model: $ORBITON_LLM_MODEL"
echo ""

curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$ORBITON_LLM_MODEL\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": \"Hello! Please respond with 'API is working!' if you receive this.\"
      }
    ],
    \"temperature\": 0.7,
    \"max_tokens\": 100
  }" | jq '.'

echo -e "\n======================================"
echo "Test completed!"
