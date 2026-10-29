#!/bin/bash
# 1-Tap Cloud TV Converter CLI for Termux / Bash
# Triggers GitHub Cloud Runner for GoFile or direct URLs

set -e

REPO="OddBoyXD/bravia-tv-converter"
URL="$1"
MODE="${2:-video}"

if [ -z "$URL" ]; then
  echo "Usage: ./convert_cli.sh <GOFILE_OR_DIRECT_URL> [video|audio]"
  echo "Example: ./convert_cli.sh 'https://gofile.io/d/YvXabCy1'"
  exit 1
fi

echo "=============================================="
echo "📺 Sony Bravia 720p Cloud Converter"
echo "Target URL: $URL"
echo "Output Mode: $MODE"
echo "=============================================="

echo "[*] Triggering GitHub Actions Cloud Runner on $REPO..."
gh workflow run convert.yml \
  --repo "$REPO" \
  -f media_url="$URL" \
  -f mode="$MODE"

echo "[+] Cloud workflow dispatched successfully!"
echo "[*] Watching cloud conversion progress..."

sleep 4
RUN_ID=$(gh run list --repo "$REPO" --workflow=convert.yml --limit 1 --json databaseId --jq '.[0].databaseId')

if [ -n "$RUN_ID" ]; then
  echo "[+] Active Cloud Run ID: $RUN_ID"
  gh run watch "$RUN_ID" --repo "$REPO"
  
  echo ""
  echo "🎉 Conversion Finished!"
  echo "Fetching direct download link..."
  gh release list --repo "$REPO" --limit 1
  
  LATEST_TAG=$(gh release list --repo "$REPO" --limit 1 | awk '{print $1}')
  echo ""
  echo "⬇️ Direct Download Link:"
  gh release view "$LATEST_TAG" --repo "$REPO" --json assets --jq '.assets[0].url'
fi
