#!/bin/bash

# Function to calculate distance between two GPS coordinates using Haversine formula
calculate_distance() {
    local lat1=$1
    local lon1=$2
    local lat2=$3
    local lon2=$4
    
    # If any coordinate is 0 or empty, return 0
    if [[ "$lat1" == "0" || "$lat1" == "0.0" || -z "$lat1" || 
          "$lon1" == "0" || "$lon1" == "0.0" || -z "$lon1" ||
          "$lat2" == "0" || "$lat2" == "0.0" || -z "$lat2" ||
          "$lon2" == "0" || "$lon2" == "0.0" || -z "$lon2" ]]; then
        echo "0"
        return
    fi
    
    # Convert to radians and calculate using awk for floating point arithmetic
    awk -v lat1="$lat1" -v lon1="$lon1" -v lat2="$lat2" -v lon2="$lon2" '
    BEGIN {
        pi = 3.14159265358979323846
        R = 6371000  # Earth radius in meters
        
        # Convert degrees to radians
        lat1_rad = lat1 * pi / 180
        lon1_rad = lon1 * pi / 180
        lat2_rad = lat2 * pi / 180
        lon2_rad = lon2 * pi / 180
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat/2)^2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)^2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        printf "%.1f", distance
    }'
}

# Cleanup on shutdown or reboot
cleanup() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S')\tShutting down GPS polling..." >> "$LOGFILE"
    # Clean up any temporary files
    rm -f "${GPSFILE}.tmp"
    exit 0
}

# Function to validate GPS coordinates
is_valid_coordinate() {
    local value="$1"
    # Check if it's a valid number and not null/empty/zero
    if [[ "$value" =~ ^-?[0-9]+\.?[0-9]*$ ]] && [[ "$value" != "0" ]] && [[ "$value" != "0.0" ]] && [[ "$value" != "null" ]]; then
        return 0
    fi
    return 1
}

# Function to safely write JSON to GPS file with atomic operations
write_gps_file() {
    local json_content="$1"
    local temp_file="${GPSFILE}.tmp"
    
    # Write to temp file first, then move (atomic operation)
    echo "$json_content" > "$temp_file" && mv "$temp_file" "$GPSFILE"
}

LOGFILE="/home/pi/gps_log_$(date '+%Y%m%d').txt"
GPSFILE="/home/pi/gps_fix.txt"
INTERVAL=15  # seconds between checks

echo -e "$(date '+%Y-%m-%d %H:%M:%S')\tStarting GPS polling..." >> "$LOGFILE"

# Trap shutdown or reboot signals
trap cleanup SIGTERM SIGINT

UPTIME=$(uptime -p | sed 's/^up //')
TIME=$(date '+%Y-%m-%d %H:%M:%S')
# Create the GPS file with atomic write
write_gps_file "{\"time\":\"$TIME\", \"uptime\":\"$UPTIME\", \"lat\":0,\"lon\":0,\"mode\":0,\"distance\":0}"

last_lat=0
last_lon=0
last_fix=0  # 0 = false, 1 = true

while true; do
    UPTIME=$(uptime -p | sed 's/^up //')
    TIME=$(date '+%Y-%m-%d %H:%M:%S')

    # Add error handling for gpspipe
    if ! JSON=$(timeout 30 gpspipe -w -n 10 2>/dev/null | grep TPV | head -n 1); then
        echo -e "$TIME\tWarning: gpspipe failed or timed out" >> "$LOGFILE"
        sleep "$INTERVAL"
        continue
    fi

    if [[ -n "$JSON" ]]; then
        # Validate JSON and extract values with error handling
        if ! MODE=$(echo "$JSON" | jq -r '.mode // 0' 2>/dev/null); then
            echo -e "$TIME\tWarning: Failed to parse JSON" >> "$LOGFILE"
            sleep "$INTERVAL"
            continue
        fi
        
        LAT=$(echo "$JSON" | jq -r '.lat // "0"' 2>/dev/null)
        LON=$(echo "$JSON" | jq -r '.lon // "0"' 2>/dev/null)
        
        # Convert null values to "0"
        [[ "$LAT" == "null" || "$LAT" == "empty" || -z "$LAT" ]] && LAT="0"
        [[ "$LON" == "null" || "$LON" == "empty" || -z "$LON" ]] && LON="0"
        
        # Check for valid GPS fix using improved validation
        if [[ "$MODE" -ge 2 ]] && is_valid_coordinate "$LAT" && is_valid_coordinate "$LON"; then
            if [ $last_fix -eq 0 ]; then
                echo -e "$TIME\t✔ GPS fix acquired (uptime: $UPTIME)" >> "$LOGFILE"
            fi
            if [[ "$LAT" != "$last_lat" || "$LON" != "$last_lon" ]]; then
                # If the coordinates have changed
                # Calculate distance from last position
                distance=$(calculate_distance "$last_lat" "$last_lon" "$LAT" "$LON")
                
                last_lat="$LAT"
                last_lon="$LON"
                last_fix=1  # Set to true

                echo -e "$TIME\tMode: $MODE\tCoordinates: $LAT, $LON\tDistance: ${distance}m" >> "$LOGFILE"
                write_gps_file "{\"time\":\"$TIME\", \"uptime\":\"$UPTIME\", \"lat\":$LAT,\"lon\":$LON,\"mode\":$MODE,\"distance\":$distance}"
                # break  # Exit the loop after logging the fix
            fi
        elif [ $last_fix -eq 1 ]; then
            # If we had a fix before but now we don't, log the loss of fix
            echo -e "$TIME\t✘ GPS fix lost (uptime: $UPTIME)" >> "$LOGFILE"
            last_fix=0  # Reset last_fix to false
            last_lat=0
            last_lon=0
            write_gps_file "{\"time\":\"$TIME\", \"uptime\":\"$UPTIME\", \"lat\":0,\"lon\":0,\"mode\":0,\"distance\":0}"
        fi
    fi

    sleep "$INTERVAL"
done

echo -e "$(date '+%Y-%m-%d %H:%M:%S')\tExiting GPS polling..." >> "$LOGFILE"
cleanup
