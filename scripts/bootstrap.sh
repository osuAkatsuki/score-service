#!/usr/bin/env bash
set -eo pipefail

if [[ -n "$KUBERNETES" ]]; then
  source /vault/secrets/secrets.txt
fi

cd /srv/root

# await connected service availability
/scripts/await-service.sh $READ_DB_HOST $READ_DB_PORT $SERVICE_READINESS_TIMEOUT
/scripts/await-service.sh $WRITE_DB_HOST $WRITE_DB_PORT $SERVICE_READINESS_TIMEOUT

# await redis availability
/scripts/await-service.sh $REDIS_HOST $REDIS_PORT $SERVICE_READINESS_TIMEOUT


# run the service
exec /scripts/run-service.sh