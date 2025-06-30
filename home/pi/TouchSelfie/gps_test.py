#!/usr/bin/env python3
"""
Quick GPS Test Script - Check once for GPS fix and exit
Connects to gpsd using raw socket (like telnet), checks for location fix, prints lat/lon if available, then exits.
Includes validation to detect potentially incorrect GPS readings.
"""

import sys
import socket
import json
import time

def is_valid_coordinate(lat, lon):
    """
    Check if coordinates are within valid ranges and not obviously wrong.
    Returns True if coordinates seem valid, False otherwise.
    """
    if lat is None or lon is None:
        return False
    
    # Basic range checks
    if not (-90 <= lat <= 90):
        return False
    if not (-180 <= lon <= 180):
        return False
    
    # Check for obvious bad values (like 0,0 which is in the ocean off Africa)
    # Allow some tolerance around 0,0 but flag exact 0,0 as suspicious
    if abs(lat) < 0.001 and abs(lon) < 0.001:
        return False
    
    return True

def validate_gps_quality(data, debug=False):
    """
    Check GPS quality indicators to detect potentially bad readings.
    Returns (is_good, quality_info) where is_good is boolean and quality_info is dict.
    """
    quality_info = {}
    is_good = True
    
    # Get basic fix info
    mode = data.get('mode', 0)
    lat = data.get('lat')
    lon = data.get('lon')
    
    quality_info['mode'] = mode
    quality_info['has_coordinates'] = lat is not None and lon is not None
    
    # Check coordinate validity
    if not is_valid_coordinate(lat, lon):
        is_good = False
        quality_info['coordinate_validity'] = 'INVALID'
    else:
        quality_info['coordinate_validity'] = 'VALID'
    
    # Check GPS dilution of precision (DOP) values if available
    # Lower is better: <1 = Ideal, 1-2 = Excellent, 2-5 = Good, 5-10 = Moderate, 10-20 = Fair, >20 = Poor
    hdop = data.get('hdop')  # Horizontal dilution of precision
    pdop = data.get('pdop')  # Position dilution of precision
    
    if hdop is not None:
        quality_info['hdop'] = hdop
        if hdop > 10:  # Poor horizontal accuracy
            is_good = False
            quality_info['hdop_status'] = 'POOR'
        elif hdop > 5:
            quality_info['hdop_status'] = 'MODERATE'
        else:
            quality_info['hdop_status'] = 'GOOD'
    
    if pdop is not None:
        quality_info['pdop'] = pdop
        if pdop > 10:  # Poor position accuracy
            quality_info['pdop_status'] = 'POOR'
        elif pdop > 5:
            quality_info['pdop_status'] = 'MODERATE'
        else:
            quality_info['pdop_status'] = 'GOOD'
    
    # Check number of satellites if available
    satellites_used = data.get('satellites', data.get('sats'))
    if satellites_used is not None:
        quality_info['satellites_used'] = satellites_used
        if satellites_used < 4:  # Need at least 4 for 3D fix
            is_good = False
            quality_info['satellite_status'] = 'INSUFFICIENT'
        elif satellites_used < 6:
            quality_info['satellite_status'] = 'MINIMAL'
        else:
            quality_info['satellite_status'] = 'GOOD'
    
    # Check estimated position error if available
    eph = data.get('eph')  # Estimated horizontal position error in meters
    
    if eph is not None:
        quality_info['eph_meters'] = eph
        if eph > 100:  # More than 100m error is concerning
            is_good = False
            quality_info['horizontal_error_status'] = 'HIGH'
        elif eph > 50:
            quality_info['horizontal_error_status'] = 'MODERATE'
        else:
            quality_info['horizontal_error_status'] = 'LOW'
    
    # Check timestamp freshness
    gps_time = data.get('time')
    if gps_time:
        quality_info['gps_time'] = gps_time
        # Could add timestamp validation here if needed
    
    if debug:
        print(f"DEBUG: GPS Quality - Good: {is_good}, Info: {quality_info}")
    
    return is_good, quality_info

def get_gps_location_raw(debug=False):
    """
    Connect to gpsd using raw socket, check for GPS fix, return coordinates if available.
    Returns (lat, lon) if fix available, None if no fix.
    """
    try:
        if debug:
            print("DEBUG: Attempting to connect to gpsd via raw socket...")
        
        # Create a socket connection (like telnet)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)  # 5 second timeout
        
        try:
            sock.connect(('localhost', 2947))
        except ConnectionRefusedError:
            if debug:
                print("DEBUG: Connection refused - gpsd may not be running")
            return None
        except OSError as e:
            if debug:
                print(f"DEBUG: Connection failed: {e}")
            return None
        
        if debug:
            print("DEBUG: Connected successfully")
        
        # Enable streaming by sending the watch command
        watch_cmd = '?WATCH={"enable":true,"json":true}\n'
        sock.send(watch_cmd.encode())
        
        if debug:
            print("DEBUG: Sent WATCH command")
        
        # Create a file object for easier line reading
        sock_file = sock.makefile('r')
        
        # Read responses and look for TPV messages
        max_attempts = 20
        attempts = 0
        start_time = time.time()
        max_time = 10.0  # Maximum time to spend trying (10 seconds)
        
        if debug:
            print(f"DEBUG: Starting to read JSON messages (max {max_attempts} attempts, {max_time}s timeout)...")
        
        while attempts < max_attempts and (time.time() - start_time) < max_time:
            try:
                line = sock_file.readline().strip()
                
                if not line:
                    attempts += 1
                    time.sleep(0.1)
                    continue
                
                if debug and attempts % 5 == 0:
                    print(f"DEBUG: Attempt {attempts}")
                
                if debug:
                    print(f"DEBUG: Received line: {line[:100]}...")
                
                # Parse JSON
                try:
                    data = json.loads(line)
                    
                    if debug:
                        print(f"DEBUG: Parsed JSON class: {data.get('class', 'unknown')}")
                    
                    # Look for TPV messages with GPS fix
                    if data.get('class') == 'TPV':
                        mode = data.get('mode', 0)
                        lat = data.get('lat')
                        lon = data.get('lon')
                        
                        if debug:
                            print(f"DEBUG: TPV - Mode: {mode}, Lat: {lat}, Lon: {lon}")
                        
                        if mode >= 2 and lat is not None and lon is not None:
                            # Validate GPS quality before accepting the fix
                            is_good, quality_info = validate_gps_quality(data, debug)
                            if is_good:
                                if debug:
                                    print(f"DEBUG: Found valid GPS fix! Mode: {mode}, Lat: {lat}, Lon: {lon}")
                                sock_file.close()
                                sock.close()
                                return (lat, lon)
                            else:
                                if debug:
                                    print("DEBUG: Detected potentially bad GPS reading, skipping...")
                                    print(f"DEBUG: Quality issues: {quality_info}")
                                # Continue looking for a better reading
                
                except json.JSONDecodeError as e:
                    if debug:
                        print(f"DEBUG: JSON decode error: {e}")
                    continue
                
                attempts += 1
                
            except socket.timeout:
                if debug:
                    print("DEBUG: Socket timeout")
                break
            except OSError as e:
                if debug:
                    print(f"DEBUG: Exception reading data: {e}")
                break
        
        if debug:
            print(f"DEBUG: Completed {attempts} attempts, no fix found")
        
        try:
            sock_file.close()
        except (OSError, AttributeError):
            pass
        try:
            sock.close()
        except (OSError, AttributeError):
            pass
        return None
        
    except (OSError, ConnectionRefusedError) as e:
        if debug:
            print(f"DEBUG: Connection error: {e}")
        return None

def get_gps_location(debug=False):
    """
    Try both raw socket and python-gps library approaches.
    Returns (lat, lon) if fix available, None if no fix.
    """
    # First try the raw socket approach (like telnet)
    result = get_gps_location_raw(debug)
    if result:
        return result
    
    # Fallback to python-gps library if available
    try:
        import gps
    except ImportError:
        if debug:
            print("DEBUG: python3-gps library not available")
        return None
    
    if debug:
        print("DEBUG: Trying python-gps library as fallback...")
    
    try:
        # Set a short timeout for quick operation
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(2.0)  # Shorter timeout
        
        try:
            session = gps.gps("localhost", "2947")
            session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
            socket.setdefaulttimeout(original_timeout)
            
            # Try just a few attempts
            for _ in range(10):
                try:
                    report = session.next()
                    if hasattr(report, 'get') and report.get('class') == 'TPV':
                        mode = report.get('mode', 0)
                        lat = report.get('lat')
                        lon = report.get('lon')
                        if mode >= 2 and lat is not None and lon is not None:
                            session.close()
                            return (lat, lon)
                except StopIteration:
                    time.sleep(0.1)
            
            session.close()
            return None
            
        except (OSError, socket.timeout) as e:
            if debug:
                print(f"DEBUG: python-gps error: {e}")
            socket.setdefaulttimeout(original_timeout)
            return None
    
    except ImportError as e:
        if debug:
            print(f"DEBUG: Fallback error: {e}")
        return None

def main():
    """Main function - get GPS location and print result."""
    # Check command line arguments
    debug = False
    test_no_gps = False
    
    for arg in sys.argv[1:]:
        if arg == '--debug':
            debug = True
        elif arg == '--test-no-gps':
            test_no_gps = True
        elif arg in ('--help', '-h'):
            print("Usage: gps_test.py [--debug] [--test-no-gps] [--help]")
            print("  --debug      : Show detailed debug output")
            print("  --test-no-gps: Simulate no GPS connection (for testing)")
            print("  --help       : Show this help")
            return
    
    if test_no_gps:
        if debug:
            print("DEBUG: Simulating no GPS connection")
        print()  # Empty line for no fix
        return
    
    result = get_gps_location(debug)
    
    if result:
        latitude, longitude = result
        print(f"{latitude:.6f},{longitude:.6f}")
    else:
        # No fix - print empty line
        if not debug:
            print()
        else:
            print("DEBUG: No GPS fix found")

if __name__ == "__main__":
    main()