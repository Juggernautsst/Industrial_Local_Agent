#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

MODEL_ID="${MODEL_ID:-Qwen/Qwen3.8-27B-FP8}"
MODEL_REVISION="${MODEL_REVISION:-017b9c7af6b5689d5dd426a76e0bc077eb5ca20a}"
MODEL_DIR="${MODEL_DIR:-${SCRATCH:?Set SCRATCH or MODEL_DIR}/${USER:-user}/models/qwen3.8-27b-fp8}"

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

case "$MODEL_DIR" in
    /*) ;;
    *) die 'MODEL_DIR must be an absolute path on protected Linux storage' ;;
esac

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    repo_root=$(git rev-parse --show-toplevel)
    case "$MODEL_DIR" in
        "$repo_root"/*) die 'MODEL_DIR must not be inside the Git checkout' ;;
    esac
fi

mkdir -p "$MODEL_DIR"
chmod 700 "$MODEL_DIR"

if command -v hf >/dev/null 2>&1; then
    hf download "$MODEL_ID" \
        --revision "$MODEL_REVISION" \
        --local-dir "$MODEL_DIR"
elif command -v huggingface-cli >/dev/null 2>&1; then
    huggingface-cli download "$MODEL_ID" \
        --revision "$MODEL_REVISION" \
        --local-dir "$MODEL_DIR"
else
    die 'hf or huggingface-cli is required; install it in the approved Bunya environment'
fi

[[ -f "$MODEL_DIR/config.json" ]] || die "missing $MODEL_DIR/config.json"
[[ -f "$MODEL_DIR/model.safetensors.index.json" ]] || die "missing model index in $MODEL_DIR"

manifest="$MODEL_DIR/provenance.json"
MODEL_DIR="$MODEL_DIR" MODEL_ID="$MODEL_ID" MODEL_REVISION="$MODEL_REVISION" MANIFEST="$manifest" \
python3 - <<'PY'
import hashlib
import json
import os
from pathlib import Path

root = Path(os.environ["MODEL_DIR"])
files = []
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.is_symlink() or ".cache" in path.parts or path.name == "provenance.json":
        continue
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    files.append({
        "path": str(path.relative_to(root)),
        "bytes": size,
        "sha256": digest.hexdigest(),
    })

payload = {
    "schema_version": 1,
    "model_id": os.environ["MODEL_ID"],
    "revision": os.environ["MODEL_REVISION"],
    "files": files,
}
Path(os.environ["MANIFEST"]).write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
chmod 600 "$manifest"
printf 'prepared model_id=%s revision=%s files=%s manifest=%s\n' \
    "$MODEL_ID" "$MODEL_REVISION" "$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))["files"]))' "$manifest")" "$manifest"
