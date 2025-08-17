source ../.env
curl -X PUT "http://127.0.0.1:5000/ai-func/test" \
  -H "Api-Token: $AI_FUNC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{}"
