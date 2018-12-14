#!/bin/bash
set -e

function finish {
  rm ./push_logs
}
trap finish EXIT

docker build -t 7imbrook/santa .
docker push 7imbrook/santa | tee ./push_logs

# Swap shas, don't think we need this

NEW_DIGEST=$(tail -n 1 push_logs | cut -d':' -f 4 | cut -d' ' -f 1)

echo
echo "Going to deploy" $NEW_DIGEST

kubectl patch deployment django-service -p \
  "{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"santa-app\",\"image\":\"7imbrook/santa@sha256:$NEW_DIGEST\"}]}}}}"