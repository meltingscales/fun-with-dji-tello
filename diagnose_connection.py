#!/usr/bin/env python3
"""
Diagnostic script to troubleshoot Tello connection issues
"""
import socket
import time
import subprocess
import sys
import os

def check_wifi_connection():
    """Check if connected to Tello WiFi"""
    print("\n" + "="*60)
    print("1. CHECKING WIFI CONNECTION")
    print("="*60)

    try:
        # Try to get current WiFi SSID on Linux
        result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True)
        ssid = result.stdout.strip()

        if ssid:
            print(f"✓ Connected to WiFi: {ssid}")
            if 'TELLO' in ssid.upper():
                print("✓ Connected to Tello WiFi network!")
                return True
            else:
                print(f"✗ WARNING: Not connected to Tello WiFi (current: {ssid})")
                print("  Please connect to your Tello's WiFi network (TELLO-XXXXXX)")
                return False
        else:
            print("✗ Could not determine WiFi connection")
            return False
    except Exception as e:
        print(f"⚠ Could not check WiFi: {e}")
        print("  Please manually verify you're connected to Tello WiFi")
        return None

def test_udp_send():
    """Test sending UDP command to Tello"""
    print("\n" + "="*60)
    print("2. TESTING UDP COMMAND SEND (port 8889)")
    print("="*60)

    tello_address = ('192.168.10.1', 8889)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)

    try:
        print(f"Sending 'command' to {tello_address[0]}:{tello_address[1]}...")
        sock.sendto(b'command', tello_address)

        try:
            response, _ = sock.recvfrom(1024)
            print(f"✓ Received response: {response.decode('utf-8', errors='ignore')}")
            return True
        except socket.timeout:
            print("✗ No response received (timeout)")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        sock.close()

def test_state_port():
    """Test listening for state packets on port 8890"""
    print("\n" + "="*60)
    print("3. TESTING STATE PORT LISTENER (port 8890)")
    print("="*60)

    local_port = 8890

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', local_port))
        sock.settimeout(10)

        print(f"Listening on 0.0.0.0:{local_port} for state packets...")
        print("(waiting 10 seconds...)")

        try:
            data, address = sock.recvfrom(1024)
            print(f"✓ Received state packet from {address}:")
            print(f"  {data.decode('utf-8', errors='ignore')}")
            return True
        except socket.timeout:
            print("✗ No state packets received (timeout)")
            print("\nPossible issues:")
            print("  1. Firewall is blocking UDP port 8890")
            print("  2. Not connected to Tello WiFi")
            print("  3. Tello is not powered on or in range")
            return False
    except OSError as e:
        if "Address already in use" in str(e):
            print("✗ Port 8890 is already in use")
            print("  Another program might be using the port.")
            print("  Try: sudo lsof -i :8890")
        else:
            print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        sock.close()

def check_firewall():
    """Check firewall status"""
    print("\n" + "="*60)
    print("4. CHECKING FIREWALL")
    print("="*60)

    try:
        # Check ufw status
        result = subprocess.run(['sudo', 'ufw', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            if 'Status: active' in result.stdout:
                print("\n⚠ Firewall is active. You may need to allow UDP ports 8889 and 8890")
                print("  Run: sudo ufw allow 8889/udp")
                print("  Run: sudo ufw allow 8890/udp")
        else:
            print("Could not check ufw status (may not be installed)")
    except FileNotFoundError:
        print("ufw not found, checking iptables...")
        try:
            result = subprocess.run(['sudo', 'iptables', '-L'], capture_output=True, text=True)
            if result.returncode == 0:
                print("iptables rules exist (output truncated)")
                print("You may need to allow UDP ports 8889 and 8890")
        except:
            print("Could not check firewall status")

def main():
    print("\n" + "="*60)
    print("DJI TELLO CONNECTION DIAGNOSTIC TOOL")
    print("="*60)
    print("\nThis script will help diagnose connection issues with your Tello.\n")

    # Run diagnostics
    wifi_ok = check_wifi_connection()
    time.sleep(1)

    command_ok = test_udp_send()
    time.sleep(1)

    state_ok = test_state_port()
    time.sleep(1)

    check_firewall()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if wifi_ok == False:
        print("\n❌ PRIMARY ISSUE: Not connected to Tello WiFi")
        print("   → Connect to your Tello's WiFi network (TELLO-XXXXXX)")
    elif not command_ok:
        print("\n❌ PRIMARY ISSUE: Cannot send commands to Tello")
        print("   → Check that Tello is powered on and WiFi is connected")
    elif not state_ok:
        print("\n❌ PRIMARY ISSUE: Not receiving state packets")
        print("   → Likely a firewall issue blocking UDP port 8890")
        print("\n   RECOMMENDED FIXES:")
        print("   1. Allow UDP ports in firewall:")
        print("      sudo ufw allow 8889/udp")
        print("      sudo ufw allow 8890/udp")
        print("   2. Or temporarily disable firewall (not recommended):")
        print("      sudo ufw disable")
        print("   3. Check if another program is using port 8890:")
        print("      sudo lsof -i :8890")
    else:
        print("\n✓ All checks passed! Connection should work.")

    print("\n" + "="*60)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Note: Some checks require sudo privileges")
        print("Consider running: sudo python diagnose_connection.py\n")
    main()
