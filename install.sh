#!/usr/bin/env sh
set -eu

SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DESTINATION=${1:-"${CODEX_HOME:-$HOME/.codex}/skills/novel-writing-engine"}
MODE=${2:-}

case "$DESTINATION" in
  "$SOURCE_DIR"|"$SOURCE_DIR"/*)
    echo "Destination must not be the source directory or a directory inside it." >&2
    exit 3
    ;;
esac

if [ -e "$DESTINATION" ] && [ "$MODE" != "--update" ]; then
  echo "Destination already exists: $DESTINATION. Pass --update to copy updated files without deleting existing files." >&2
  exit 2
fi

mkdir -p "$DESTINATION"
for item in "$SOURCE_DIR"/* "$SOURCE_DIR"/.[!.]*; do
  [ -e "$item" ] || continue
  name=$(basename "$item")
  case "$name" in
    .git|work|__pycache__) continue ;;
  esac
  cp -R "$item" "$DESTINATION/"
done

echo "Installed novel-writing-engine to $DESTINATION"
