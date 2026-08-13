#!/bin/sh
set -e

if [ -z "$AUTH_USER" ] || [ -z "$AUTH_PASS" ]; then
  echo "ERROR: AUTH_USER and AUTH_PASS must be set to enable Basic Auth." >&2
  echo "       Add them to the root .env file." >&2
  exit 1
fi

htpasswd -cb /etc/nginx/.htpasswd "$AUTH_USER" "$AUTH_PASS"
echo "Basic Auth enabled for user: $AUTH_USER"

exec "$@"
