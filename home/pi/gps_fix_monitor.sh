#!/bin/bash

LOGFILE=~/gps_fix_log.txt
INTERVAL=5  # seconds between checks

echo -n > "$LOGFILE"  # Clear the log file
echo "Monitoring GPS fix status..."
echo "Started at $(date)" >> "$LOGFILE"
echo "Waiting for GPS fix..." >> "$LOGFILE"

while true; do
  JSON=$(gpspipe -w -n 10 | grep TPV | head -n 1)

  if [[ -n "$JSON" ]]; then
    MODE=$(echo "$JSON" | jq -r '.mode // 0')
    LAT=$(echo "$JSON" | jq -r '.lat // empty')
    LON=$(echo "$JSON" | jq -r '.lon // empty')

    echo "$(date): mode=$MODE lat=$LAT lon=$LON" >> "$LOGFILE"

    if [[ "$MODE" -ge 2 && "$LAT" != "0.0" && "$LAT" != "0" && "$LON" != "0.0" && "$LON" != "0" ]]; then
      UPTIME=$(uptime -p | sed 's/^up //')
      TIME=$(date +"%Y-%m-%d %H:%M:%S")
      echo "✔ GPS fix acquired at $TIME (uptime: $UPTIME)"
      echo "Fix time: $TIME (uptime: $UPTIME)" >> "$LOGFILE"
      echo "Coordinates: $LAT, $LON" >> "$LOGFILE"
      break
    fi
  fi

  sleep "$INTERVAL"
done