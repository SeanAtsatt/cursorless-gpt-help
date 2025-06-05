#!/bin/zsh

DEBUG=false

# Handle optional --debug flag
if [[ "$1" == "--debug" ]]; then
  DEBUG=true
  shift
fi

while true; do
  echo -n "askgpt: "
  read question

  if [[ -z "$question" ]]; then
    echo "Goodbye!"
    break
  fi

  response=$(curl -s -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"$question\"}")

  echo
  if $DEBUG; then
    echo "[RAW RESPONSE]:"
    echo "$response"
    echo
  fi

  if echo "$response" | jq -e .answer > /dev/null 2>&1; then
    echo "$response" | jq -r .answer
  else
    echo "⚠️  Unexpected response:"
    echo "$response"
  fi
  echo
done
