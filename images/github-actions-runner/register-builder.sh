#!/usr/bin/env bash

set -e
set -x

function show_usage() {
  cat << EOF
TODO
EOF
}

CONFIG_FILE=""
TOKEN_FILE=""
SHOULD_RUN=""
RUN_ONCE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      shift
      CONFIG_FILE="$1"
      shift
      ;;
    --token-file)
      shift
      TOKEN_FILE="$1"
      shift
      ;;
    --run)
      shift
      SHOULD_RUN="true"
      ;;
    --once)
      shift
      RUN_ONCE="true"
      ;;
    -h|--help)
      show_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
  esac
done


if [ ! -f "$CONFIG_FILE" ]; then
  echo "bad config file ($CONFIG_FILE)..."
  exit 1
fi
if [ ! -f "$TOKEN_FILE" ]; then
  echo "bad config file ($TOKEN_FILE)..."
  exit 1
fi
set -x

WORKER_INSTALL="$(jq -r .install $CONFIG_FILE)"
WORKER_NAME="$(jq -r .name $CONFIG_FILE)"
WORKER_DIR="$(jq -r .work $CONFIG_FILE)"
REPO_OWNER="$(jq -r .owner $CONFIG_FILE)"
REPO_NAME="$(jq -r .repo $CONFIG_FILE)"
LABELS="$(jq -r -c .labels[] $CONFIG_FILE | tr '\n' ',' | sed 's/,$/\n/')"
PACKAGE_URL="$(jq -r -c .download_url $CONFIG_FILE)"
REGISTER_URL="https://github.com/$REPO_OWNER/$REPO_NAME"
/github-utils/github-auth.py create  --set --repo=$REPO_NAME --owner=$REPO_OWNER --token=$(cat $TOKEN_FILE) -f /tmp/default_auth.json
REGISTER_TOKEN="$(/github-utils/github-actions-api.py registration-token | jq -r .token)"

if [ "$PACKAGE_URL" == "" ]; then
  PACKAGE_URL="$(/github-utils/github-actions-api.py downloads | jq -r .download_url)"
fi

cd $WORKER_INSTALL
sudo ln -s $WORKER_INSTALL /worker-root
if [ ! -d "$WORKER_DIR" ]; then
  sudo mkdir $WORKER_DIR
fi
sudo chown actions-runner $WORKER_DIR
wget -q -O - "$PACKAGE_URL" | tar xzf -

./config.sh --unattended \
   --url "$REGISTER_URL" \
   --token "$REGISTER_TOKEN" \
   --name $WORKER_NAME \
   --work $WORKER_DIR \
   --labels "$LABELS" \
   --replace

if [ "$SHOULD_RUN" != "true" ]; then
  exit 0
fi

if [ "$RUN_ONCE" != "true" ]; then
  ./run.sh
  exit $?
fi

while true; do
  ./run.sh --once
  rm -rf "${WORKER_DIR}/actions/*"
fi

