#!/usr/bin/env python3

import os
import glob
import re
import sys
import json
from datetime import datetime
from pathlib import Path
import subprocess

class SpaceEngineersDiagnostics:
    def __init__(self):
        self.home = str(Path.home())
        self.se_appid = "244850"
        self.log_patterns = {
            "crash": r"(?i)(crash|exception|error|fatal)",
            "memory": r"(?i)(out of memory|memory allocation|memory error)",
            "directx": r"(?i)(directx|d3d|graphics device)",
            "proton": r"(?i)(proton|wine|steam\.exe)",
        }
        
    def find_game_directory(self):
        """Find Space Engineers installation directory"""
        compatdata_path = os.path.join(self.home, ".steam/steam/steamapps/compatdata", self.se_appid)
        pfx_path = os.path.join(compatdata_path, "pfx/drive_c/users/steamuser/Application Data/SpaceEngineers")
        return pfx_path if os.path.exists(pfx_path) else None

    def get_system_info(self):
        """Gather system information"""
        info = {}
        try:
            # Get CPU info
            with open("/proc/cpuinfo") as f:
                cpu_info = f.read()
                info["cpu_model"] = re.search(r"model name\s+: (.+)", cpu_info).group(1)
                info["cpu_cores"] = len(re.findall(r"processor\s+:", cpu_info))

            # Get RAM info
            with open("/proc/meminfo") as f:
                mem_info = f.read()
                total_mem = int(re.search(r"MemTotal:\s+(\d+)", mem_info).group(1)) // 1024
                info["total_memory_mb"] = total_mem

            # Get GPU info
            gpu_info = subprocess.check_output(["lspci", "-v"]).decode()
            gpu_match = re.search(r"VGA compatible controller: (.+)", gpu_info)
            if gpu_match:
                info["gpu"] = gpu_match.group(1)

            # Get Linux distribution info
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    os_info = {}
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            os_info[key] = value.strip('"')
                    info["os"] = f"{os_info.get('NAME', 'Unknown')} {os_info.get('VERSION_ID', '')}"

        except Exception as e:
            print(f"Error gathering system information: {e}")

        return info

    def analyze_logs(self):
        """Analyze Space Engineers log files"""
        game_dir = self.find_game_directory()
        if not game_dir:
            print("Could not find Space Engineers directory!")
            return

        log_files = glob.glob(os.path.join(game_dir, "*.log"))
        crash_reports = []

        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for different types of issues
                    for issue_type, pattern in self.log_patterns.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Get context around the error (up to 5 lines)
                            lines = content.split('\n')
                            line_num = content[:match.start()].count('\n')
                            context_start = max(0, line_num - 2)
                            context_end = min(len(lines), line_num + 3)
                            context = '\n'.join(lines[context_start:context_end])
                            
                            crash_reports.append({
                                "file": os.path.basename(log_file),
                                "type": issue_type,
                                "context": context,
                                "timestamp": datetime.fromtimestamp(os.path.getmtime(log_file)).isoformat()
                            })
            except Exception as e:
                print(f"Error reading log file {log_file}: {e}")

        return crash_reports

    def check_proton_version(self):
        """Check Proton version and configuration"""
        try:
            compatdata_path = os.path.join(self.home, ".steam/steam/steamapps/compatdata", self.se_appid)
            version_file = os.path.join(compatdata_path, "version")
            
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    return f.read().strip()
            return "Unknown"
        except Exception as e:
            return f"Error checking Proton version: {e}"

    def run_diagnostics(self):
        """Run all diagnostics and print results"""
        print("\n=== Space Engineers Diagnostics Report ===\n")
        
        # System Information
        print("System Information:")
        system_info = self.get_system_info()
        for key, value in system_info.items():
            print(f"  {key}: {value}")

        # Proton Version
        print("\nProton Version:")
        proton_version = self.check_proton_version()
        print(f"  {proton_version}")

        # Log Analysis
        print("\nAnalyzing crash logs...")
        crash_reports = self.analyze_logs()
        
        if crash_reports:
            print(f"\nFound {len(crash_reports)} potential issues:")
            for report in crash_reports:
                print(f"\nIssue Type: {report['type']}")
                print(f"File: {report['file']}")
                print(f"Timestamp: {report['timestamp']}")
                print("Context:")
                print(report['context'])
        else:
            print("\nNo crash reports found.")

        # Recommendations
        print("\nRecommendations:")
        self.provide_recommendations(system_info, crash_reports)

    def provide_recommendations(self, system_info, crash_reports):
        """Provide recommendations based on analysis"""
        if not crash_reports:
            print("- No specific issues found in logs. If crashes persist:")
            print("  * Verify game files through Steam")
            print("  * Try different Proton versions")
            return

        issue_types = [report['type'] for report in crash_reports]
        
        if 'memory' in issue_types:
            print("- Possible memory-related issues detected:")
            print("  * Consider closing other applications while playing")
            print("  * Verify your system meets the minimum requirements")

        if 'directx' in issue_types:
            print("- Graphics-related issues detected:")
            print("  * Try forcing DirectX 11 mode")
            print("  * Update graphics drivers")
            print("  * Consider using different Proton versions")

        if 'proton' in issue_types:
            print("- Proton-specific issues detected:")
            print("  * Try using a different Proton version")
            print("  * Verify DXVK is properly installed")
            print("  * Check Steam Play compatibility settings")

def main():
    diagnostics = SpaceEngineersDiagnostics()
    diagnostics.run_diagnostics()

if __name__ == "__main__":
    main() 