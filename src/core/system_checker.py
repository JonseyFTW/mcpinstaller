"""
System compatibility checker for MCP Installer
Checks and installs prerequisites automatically
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# Windows-specific imports (optional)
try:
    import winreg
    WINDOWS_REGISTRY_AVAILABLE = True
except ImportError:
    WINDOWS_REGISTRY_AVAILABLE = False
from typing import Dict, List, Tuple, Optional
import json
import requests

from ..utils.logger import get_logger


class SystemChecker:
    """Comprehensive system compatibility checker"""
    
    def __init__(self):
        self.logger = get_logger()
        self.results = {}
        self.auto_fix = True  # Enable auto-fix by default
        
    def check_all(self) -> Dict[str, Dict]:
        """Run all system checks and return results"""
        self.logger.info("Starting comprehensive system check", category="system")
        
        checks = [
            ("python", self.check_python),
            ("platform", self.check_platform),
            ("disk_space", self.check_disk_space),
            ("internet", self.check_internet_connectivity),
            ("node_js", self.check_nodejs),
            ("winget", self.check_winget),
            ("ides", self.check_ides),
            ("docker", self.check_docker)
        ]
        
        for check_name, check_func in checks:
            try:
                self.logger.info(f"Running check: {check_name}", category="system")
                result = check_func()
                self.results[check_name] = result
                self.logger.log_system_info(
                    check_name, 
                    "PASS" if result["status"] else "FAIL", 
                    result.get("details", "")
                )
            except Exception as e:
                self.logger.error(f"Check {check_name} failed", e, category="system")
                self.results[check_name] = {
                    "status": False,
                    "message": f"Check failed: {str(e)}",
                    "details": str(e)
                }
        
        return self.results
    
    def check_python(self) -> Dict:
        """Check Python installation and version"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version >= (3, 8):
            return {
                "status": True,
                "message": f"Python {version_str} is compatible",
                "details": f"Version: {version_str}, Executable: {sys.executable}"
            }
        else:
            return {
                "status": False,
                "message": f"Python {version_str} is too old (need 3.8+)",
                "details": f"Current: {version_str}, Required: 3.8+"
            }
    
    def check_platform(self) -> Dict:
        """Check operating system compatibility"""
        system = platform.system()
        release = platform.release()
        version = platform.version()
        
        if system == "Windows":
            # Check Windows version
            try:
                version_info = sys.getwindowsversion()
                if version_info.major >= 10:
                    return {
                        "status": True,
                        "message": f"Windows {release} is supported",
                        "details": f"OS: {system} {release}, Version: {version}"
                    }
                else:
                    return {
                        "status": False,
                        "message": f"Windows {release} is not supported (need Windows 10+)",
                        "details": f"Current: {system} {release}"
                    }
            except AttributeError:
                # Non-Windows platform
                pass
        
        return {
            "status": True,
            "message": f"Platform {system} detected",
            "details": f"OS: {system} {release}, Version: {version}"
        }
    
    def check_disk_space(self) -> Dict:
        """Check available disk space"""
        try:
            # Get disk usage for current drive
            if platform.system() == "Windows":
                drive = Path.cwd().drive
                usage = shutil.disk_usage(drive)
            else:
                usage = shutil.disk_usage("/")
            
            free_gb = usage.free / (1024**3)
            total_gb = usage.total / (1024**3)
            
            required_gb = 2.0  # Minimum 2GB required
            
            if free_gb >= required_gb:
                return {
                    "status": True,
                    "message": f"{free_gb:.1f} GB available (sufficient)",
                    "details": f"Free: {free_gb:.1f} GB, Total: {total_gb:.1f} GB, Required: {required_gb} GB"
                }
            else:
                return {
                    "status": False,
                    "message": f"Insufficient disk space: {free_gb:.1f} GB (need {required_gb} GB)",
                    "details": f"Free: {free_gb:.1f} GB, Required: {required_gb} GB"
                }
        except Exception as e:
            return {
                "status": False,
                "message": f"Could not check disk space: {str(e)}",
                "details": str(e)
            }
    
    def check_internet_connectivity(self) -> Dict:
        """Check internet connectivity with multiple methods"""
        # Try multiple approaches to test connectivity
        test_urls = [
            "https://api.github.com",
            "https://www.google.com", 
            "https://httpbin.org/status/200",
            "https://registry.npmjs.org"
        ]
        
        # Method 1: Try requests if available
        try:
            import requests
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=8)
                    if response.status_code == 200:
                        return {
                            "status": True,
                            "message": "Internet connectivity available",
                            "details": f"Successfully connected to {url} (HTTP {response.status_code})"
                        }
                except requests.exceptions.RequestException as e:
                    self.logger.debug(f"Failed to connect to {url}: {e}", category="system")
                    continue
                    
        except ImportError:
            self.logger.debug("requests module not available, trying alternative methods", category="system")
        
        # Method 2: Try using urllib (built-in)
        try:
            import urllib.request
            import urllib.error
            
            for url in test_urls:
                try:
                    with urllib.request.urlopen(url, timeout=8) as response:
                        if response.getcode() == 200:
                            return {
                                "status": True,
                                "message": "Internet connectivity available",
                                "details": f"Successfully connected to {url} via urllib (HTTP {response.getcode()})"
                            }
                except (urllib.error.URLError, urllib.error.HTTPError) as e:
                    self.logger.debug(f"urllib failed to connect to {url}: {e}", category="system")
                    continue
        except Exception as e:
            self.logger.debug(f"urllib method failed: {e}", category="system")
        
        # Method 3: Try ping as fallback (Windows/Linux compatible)
        try:
            ping_targets = ["8.8.8.8", "1.1.1.1", "google.com"]
            
            for target in ping_targets:
                ping_cmd = ["ping", "-n", "1", target] if platform.system() == "Windows" else ["ping", "-c", "1", target]
                
                try:
                    result = subprocess.run(
                        ping_cmd,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                    )
                    
                    if result.returncode == 0:
                        return {
                            "status": True,
                            "message": "Internet connectivity available",
                            "details": f"Ping to {target} successful (fallback method)"
                        }
                except subprocess.TimeoutExpired:
                    continue
                except Exception as e:
                    self.logger.debug(f"Ping to {target} failed: {e}", category="system")
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Ping method failed: {e}", category="system")
        
        # All methods failed
        return {
            "status": False,
            "message": "Internet connectivity test failed",
            "details": "Could not reach any test servers. Check your internet connection and firewall settings."
        }
    
    def check_nodejs(self) -> Dict:
        """Check Node.js installation and version with improved detection"""
        # First try multiple node command variations
        node_commands = ["node", "nodejs"]
        
        for node_cmd in node_commands:
            try:
                # Use proper subprocess flags for Windows
                creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                
                result = subprocess.run(
                    [node_cmd, "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=15,
                    creationflags=creationflags,
                    shell=False
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.logger.info(f"Found Node.js with '{node_cmd}': {version}", category="system")
                    
                    # Extract version number (remove 'v' prefix)
                    try:
                        version_num = version.lstrip('v')
                        major_version = int(version_num.split('.')[0])
                        
                        if major_version >= 16:  # Lower requirement for better compatibility
                            # Also check npm
                            npm_result = subprocess.run(
                                ["npm", "--version"],
                                capture_output=True,
                                text=True,
                                timeout=10,
                                creationflags=creationflags
                            )
                            
                            npm_info = f", npm: {npm_result.stdout.strip()}" if npm_result.returncode == 0 else ""
                            
                            return {
                                "status": True,
                                "message": f"Node.js {version} is installed",
                                "details": f"Command: {node_cmd}, Version: {version}{npm_info}"
                            }
                        else:
                            message = f"Node.js {version} is too old (need v16+)"
                            if self.auto_fix:
                                return self._install_nodejs()
                            else:
                                return {
                                    "status": False,
                                    "message": message,
                                    "details": f"Current: {version}, Required: v16+"
                                }
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"Could not parse Node.js version '{version}': {e}", category="system")
                        # If we can't parse version but command works, assume it's good
                        return {
                            "status": True,
                            "message": f"Node.js {version} detected (version parsing failed)",
                            "details": f"Command: {node_cmd}, Raw version: {version}"
                        }
                        
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Node.js check with '{node_cmd}' timed out", category="system")
                continue
            except FileNotFoundError:
                self.logger.debug(f"Node.js command '{node_cmd}' not found", category="system")
                continue
            except Exception as e:
                self.logger.warning(f"Node.js check with '{node_cmd}' failed: {e}", category="system")
                continue
        
        # If no node command worked, try checking common installation paths
        if platform.system() == "Windows":
            common_paths = [
                Path(os.environ.get("PROGRAMFILES", "")) / "nodejs" / "node.exe",
                Path(os.environ.get("PROGRAMFILES(X86)", "")) / "nodejs" / "node.exe",
                Path(os.environ.get("APPDATA", "")) / "npm" / "node.exe",
                Path(os.environ.get("LOCALAPPDATA", "")) / "nvs" / "default" / "node.exe"
            ]
            
            for path in common_paths:
                if path.exists():
                    try:
                        result = subprocess.run(
                            [str(path), "--version"],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        if result.returncode == 0:
                            version = result.stdout.strip()
                            return {
                                "status": True,
                                "message": f"Node.js {version} found at {path}",
                                "details": f"Path: {path}, Version: {version} (not in PATH)"
                            }
                    except Exception as e:
                        self.logger.debug(f"Failed to check Node.js at {path}: {e}", category="system")
        
        # Node.js not found anywhere
        if self.auto_fix:
            return self._install_nodejs()
        else:
            return {
                "status": False,
                "message": "Node.js not found",
                "details": "Node.js is not installed or not accessible. Please install from https://nodejs.org"
            }
    
    def check_winget(self) -> Dict:
        """Check Windows Package Manager (winget)"""
        if platform.system() != "Windows":
            return {
                "status": True,
                "message": "winget not applicable (non-Windows)",
                "details": "Windows Package Manager is Windows-specific"
            }
        
        try:
            result = subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                return {
                    "status": True,
                    "message": f"winget {version} is available",
                    "details": f"Version: {version}"
                }
            else:
                if self.auto_fix:
                    return self._install_winget()
                else:
                    return {
                        "status": False,
                        "message": "winget not available",
                        "details": "Windows Package Manager not installed"
                    }
                    
        except Exception as e:
            if self.auto_fix:
                return self._install_winget()
            else:
                return {
                    "status": False,
                    "message": f"winget check failed: {str(e)}",
                    "details": str(e)
                }
    
    def check_ides(self) -> Dict:
        """Check for installed IDEs and MCP-compatible extensions"""
        ides_found = []
        
        # Check for VS Code
        vscode_info = self._check_vscode()
        if vscode_info:
            ides_found.append(vscode_info)
        
        # Check for Cursor
        cursor_info = self._check_cursor()
        if cursor_info:
            ides_found.append(cursor_info)
        
        # Check for Windsurf
        windsurf_info = self._check_windsurf()
        if windsurf_info:
            ides_found.append(windsurf_info)
        
        # Check for Claude Desktop
        claude_info = self._check_claude_desktop()
        if claude_info:
            ides_found.append(claude_info)
        
        # Check for Claude Code (VS Code Extension/CLI)
        claude_code_info = self._check_claude_code()
        if claude_code_info:
            ides_found.append(claude_code_info)
        
        if ides_found:
            details = "; ".join([f"{ide['name']} ({ide['version']})" for ide in ides_found])
            return {
                "status": True,
                "message": f"Found {len(ides_found)} compatible IDE(s)",
                "details": details,
                "ides": ides_found
            }
        else:
            return {
                "status": False,
                "message": "No compatible IDEs found",
                "details": "Install VS Code, Cursor, Windsurf, Claude Desktop, or Claude Code for MCP support"
            }
    
    def check_docker(self) -> Dict:
        """Check Docker installation and daemon status"""
        try:
            # First check if docker command is available
            creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            
            # Check Docker version
            version_result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=creationflags
            )
            
            if version_result.returncode != 0:
                return {
                    "status": False,
                    "message": "Docker not installed",
                    "details": "Docker is not installed. Required for Docker-based MCP servers."
                }
            
            version = version_result.stdout.strip()
            self.logger.info(f"Docker version detected: {version}", category="system")
            
            # Check if Docker daemon is running
            daemon_result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=creationflags
            )
            
            if daemon_result.returncode == 0:
                # Parse some useful info from docker info
                info_lines = daemon_result.stdout.split('\n')
                containers_line = next((line for line in info_lines if 'Containers:' in line), '')
                images_line = next((line for line in info_lines if 'Images:' in line), '')
                
                details_parts = [f"Version: {version}"]
                if containers_line:
                    details_parts.append(containers_line.strip())
                if images_line:
                    details_parts.append(images_line.strip())
                
                return {
                    "status": True,
                    "message": "Docker installed and running",
                    "details": ", ".join(details_parts),
                    "daemon_running": True
                }
            else:
                # Docker is installed but daemon not running
                return {
                    "status": False,
                    "message": "Docker installed but not running",
                    "details": f"{version} - Docker daemon is not running. Start Docker Desktop or Docker service.",
                    "daemon_running": False,
                    "installed": True
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": False,
                "message": "Docker check timed out",
                "details": "Docker command timed out. Docker may be starting or unresponsive."
            }
        except FileNotFoundError:
            return {
                "status": False,
                "message": "Docker not installed",
                "details": "Docker command not found. Install Docker Desktop or Docker Engine."
            }
        except Exception as e:
            self.logger.warning(f"Docker check failed: {e}", category="system")
            return {
                "status": False,
                "message": "Docker check failed",
                "details": f"Error checking Docker: {str(e)}"
            }
    
    def _check_vscode(self) -> Optional[Dict]:
        """Check for VS Code installation without opening the application"""
        if platform.system() == "Windows":
            # Check common VS Code installation paths
            possible_paths = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "Code.exe",
                Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft VS Code" / "Code.exe",
                Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft VS Code" / "Code.exe"
            ]
            
            for path in possible_paths:
                if path.exists():
                    # Get version from resources file instead of running the executable
                    version = "Unknown"
                    try:
                        # Try to read version from package.json if available
                        resources_path = path.parent / "resources" / "app" / "package.json"
                        if resources_path.exists():
                            with open(resources_path, 'r', encoding='utf-8') as f:
                                package_data = json.load(f)
                                version = package_data.get('version', 'Unknown')
                                self.logger.info(f"VS Code version from package.json: {version}", category="system")
                        else:
                            # Try alternative locations for version info
                            version_file_paths = [
                                path.parent / "version",
                                path.parent / "resources" / "version"
                            ]
                            
                            for version_file in version_file_paths:
                                if version_file.exists():
                                    try:
                                        with open(version_file, 'r', encoding='utf-8') as f:
                                            version = f.read().strip()
                                            self.logger.info(f"VS Code version from version file: {version}", category="system")
                                            break
                                    except Exception as ve:
                                        self.logger.debug(f"Could not read version file {version_file}: {ve}", category="system")
                            
                            # If still unknown, just mark as "Installed" to avoid running the executable
                            if version == "Unknown":
                                version = "Installed"
                                self.logger.info("VS Code detected but version unknown (avoiding executable)", category="system")
                                
                    except Exception as e:
                        self.logger.debug(f"Could not determine VS Code version: {e}", category="system")
                        version = "Installed"
                    
                    # Check for MCP-compatible extensions using file system only
                    extensions = self._check_vscode_extensions()
                    
                    return {
                        "name": "VS Code",
                        "version": version,
                        "path": str(path),
                        "extensions": extensions
                    }
        else:
            # Non-Windows systems
            common_paths = [
                Path("/usr/bin/code"),
                Path("/usr/local/bin/code"),
                Path.home() / ".local" / "bin" / "code"
            ]
            
            for path in common_paths:
                if path.exists():
                    # Avoid running VS Code executable, just mark as installed
                    version = "Installed"
                    self.logger.info(f"VS Code detected at {path} (avoiding executable)", category="system")
                    
                    extensions = self._check_vscode_extensions()
                    
                    return {
                        "name": "VS Code",
                        "version": version,
                        "path": str(path),
                        "extensions": extensions
                    }
        
        return None
    
    def _get_startup_info(self):
        """Get Windows startup info to prevent window creation"""
        if platform.system() == "Windows":
            try:
                import subprocess
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                return startupinfo
            except:
                return None
        return None
    
    def _check_vscode_extensions(self) -> List[Dict]:
        """Check for MCP-compatible VS Code extensions using file system instead of CLI"""
        extensions = []
        
        # Check extension directories for all platforms
        if platform.system() == "Windows":
            possible_extension_dirs = [
                Path.home() / ".vscode" / "extensions",
                Path(os.environ.get("USERPROFILE", "")) / ".vscode" / "extensions"
            ]
        else:
            # Linux/Mac paths
            possible_extension_dirs = [
                Path.home() / ".vscode" / "extensions",
                Path.home() / ".vscode-server" / "extensions"
            ]
        
        # Look for MCP-compatible extensions
        mcp_extensions = {
            "saoudrizwan.claude-dev": "Cline",
            "rooveterinaryinc.roo-cline": "Roo"
        }
        
        for ext_dir in possible_extension_dirs:
            if ext_dir.exists():
                try:
                    self.logger.debug(f"Checking VS Code extensions in: {ext_dir}", category="system")
                    
                    for ext_id, ext_name in mcp_extensions.items():
                        # Look for extension folders that start with the extension ID
                        matching_dirs = list(ext_dir.glob(f"{ext_id}-*"))
                        if matching_dirs:
                            # Get version from folder name if possible
                            version = "installed"
                            folder_name = matching_dirs[0].name
                            
                            # Try to extract version from folder name (format: extensionid-version)
                            if '-' in folder_name:
                                version_part = folder_name.split('-')[-1]
                                # Check if version looks like a semantic version
                                if '.' in version_part and version_part.replace('.', '').replace('_', '').isdigit():
                                    version = version_part
                            
                            # Check if config file exists
                            config_path = self._get_extension_config_path(ext_name)
                            config_exists = Path(config_path).exists() if config_path else False
                            
                            extensions.append({
                                "id": ext_id,
                                "name": ext_name,
                                "status": "installed",
                                "version": version,
                                "config_path": config_path,
                                "config_exists": config_exists,
                                "folder": str(matching_dirs[0])
                            })
                            
                            self.logger.info(f"Found VS Code extension: {ext_name} v{version}", category="system")
                            
                except Exception as e:
                    self.logger.debug(f"Error checking extensions in {ext_dir}: {e}", category="system")
        
        return extensions
    
    def _get_extension_config_path(self, ext_name: str) -> str:
        """Get the MCP configuration path for VS Code extensions"""
        if platform.system() == "Windows":
            appdata = os.environ.get("APPDATA", "")
            if ext_name == "Cline":
                return os.path.join(appdata, "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json")
            elif ext_name == "Roo":
                return os.path.join(appdata, "Code", "User", "globalStorage", "rooveterinaryinc.roo-cline", "settings", "mcp_settings.json")
        else:
            # Linux/Mac paths
            home = Path.home()
            if ext_name == "Cline":
                return str(home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json")
            elif ext_name == "Roo":
                return str(home / ".config" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings" / "mcp_settings.json")
        
        return ""
    
    def _check_cursor(self) -> Optional[Dict]:
        """Check for Cursor IDE installation"""
        if platform.system() == "Windows":
            # Check common Cursor installation paths
            possible_paths = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "cursor" / "Cursor.exe",
                Path(os.environ.get("APPDATA", "")) / "Cursor" / "Cursor.exe"
            ]
        else:
            # Linux/Mac paths for Cursor
            possible_paths = [
                Path("/usr/bin/cursor"),
                Path("/usr/local/bin/cursor"),
                Path.home() / ".local" / "bin" / "cursor",
                Path("/Applications/Cursor.app/Contents/MacOS/Cursor")  # Mac
            ]
        
        for path in possible_paths:
            if path.exists():
                # Avoid running Cursor executable to prevent GUI opening
                version = "Installed"
                self.logger.info(f"Cursor detected at {path} (avoiding executable)", category="system")
                
                return {
                    "name": "Cursor",
                    "version": version,
                    "path": str(path),
                    "extensions": []
                }
        
        return None
    
    def _check_claude_desktop(self) -> Optional[Dict]:
        """Check for Claude Desktop installation"""
        if platform.system() == "Windows":
            # First, try to find Claude using Windows package management
            claude_info = self._find_claude_via_windows_packages()
            if claude_info:
                return claude_info
            
            # Fallback to file system search
            possible_paths = [
                # User installations
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Claude" / "Claude.exe",
                Path(os.environ.get("APPDATA", "")) / "Claude" / "Claude.exe",
                Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "Programs" / "Claude" / "Claude.exe",
                
                # System-wide installations
                Path(os.environ.get("PROGRAMFILES", "")) / "Claude" / "Claude.exe",
                Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Claude" / "Claude.exe",
                
                # Alternative naming patterns
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "claude-desktop" / "Claude.exe",
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ClaudeDesktop" / "Claude.exe",
                Path(os.environ.get("APPDATA", "")) / "claude-desktop" / "Claude.exe",
                
                # Check if it's in user's desktop or downloads (sometimes users put it there)
                Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "Claude.exe",
                Path(os.environ.get("USERPROFILE", "")) / "Downloads" / "Claude.exe"
            ]
        else:
            # Linux/Mac paths for Claude Desktop
            possible_paths = [
                Path("/usr/bin/claude"),
                Path("/usr/local/bin/claude"),
                Path.home() / ".local" / "bin" / "claude",
                Path("/Applications/Claude.app/Contents/MacOS/Claude"),  # Mac
                Path("/opt/Claude/claude"),  # Linux system install
                Path.home() / "Applications" / "Claude.app" / "Contents" / "MacOS" / "Claude"  # Mac user install
            ]
        
        for path in possible_paths:
            if path.exists():
                version = "Unknown"
                
                # Don't try to run Claude Desktop as it might open the GUI
                # Instead, try to find version info from files
                if platform.system() == "Windows":
                    try:
                        # Look for version info in the installation directory
                        version_files = [
                            path.parent / "version",
                            path.parent / "resources" / "app" / "package.json",
                            path.parent / "package.json"
                        ]
                        
                        for version_file in version_files:
                            if version_file.exists():
                                try:
                                    if version_file.name == "package.json":
                                        with open(version_file, 'r', encoding='utf-8') as f:
                                            package_data = json.load(f)
                                            version = package_data.get('version', 'Unknown')
                                            break
                                    else:
                                        with open(version_file, 'r', encoding='utf-8') as f:
                                            version = f.read().strip()
                                            break
                                except Exception as ve:
                                    self.logger.debug(f"Could not read version file {version_file}: {ve}", category="system")
                        
                        if version == "Unknown":
                            version = "Installed"
                            
                    except Exception as e:
                        self.logger.debug(f"Could not determine Claude Desktop version: {e}", category="system")
                        version = "Installed"
                else:
                    version = "Installed"
                
                self.logger.info(f"Claude Desktop detected at {path}", category="system")
                return {
                    "name": "Claude Desktop",
                    "version": version,
                    "path": str(path),
                    "extensions": []
                }
        
        return None
    
    def _find_claude_via_windows_packages(self) -> Optional[Dict]:
        """Find Claude using Windows package management (Get-Package, winget)"""
        try:
            # Method 1: Use PowerShell Get-Package to find Claude
            self.logger.debug("Checking for Claude via PowerShell Get-Package", category="system")
            
            ps_cmd = [
                "powershell", "-Command", 
                "Get-Package | Where-Object { $_.Name -like '*Claude*' } | Select-Object Name, Version, Source, InstallLocation | ConvertTo-Json"
            ]
            
            result = subprocess.run(
                ps_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    # Parse JSON output
                    package_data = json.loads(result.stdout.strip())
                    
                    # Handle both single package and array of packages
                    if not isinstance(package_data, list):
                        package_data = [package_data]
                    
                    for package in package_data:
                        name = package.get('Name', '')
                        if 'claude' in name.lower():
                            version = package.get('Version', 'Unknown')
                            install_location = package.get('InstallLocation', 'Unknown')
                            source = package.get('Source', 'Unknown')
                            
                            self.logger.info(f"Claude found via Get-Package: {name} v{version}", category="system")
                            
                            return {
                                "name": "Claude Desktop",
                                "version": version,
                                "path": f"Windows Package ({source})",
                                "install_location": install_location,
                                "extensions": []
                            }
                            
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Could not parse Get-Package JSON output: {e}", category="system")
                    
        except Exception as e:
            self.logger.debug(f"Get-Package check failed: {e}", category="system")
        
        # Method 2: Use winget to find Claude
        try:
            self.logger.debug("Checking for Claude via winget", category="system")
            
            winget_cmd = ["winget", "list", "claude"]
            
            result = subprocess.run(
                winget_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and "claude" in result.stdout.lower():
                # Parse winget output to extract version
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'claude' in line.lower() and not line.startswith('-'):
                        parts = line.split()
                        if len(parts) >= 3:
                            name = parts[0]
                            version = parts[2] if len(parts) > 2 else "Unknown"
                            
                            self.logger.info(f"Claude found via winget: {name} v{version}", category="system")
                            
                            return {
                                "name": "Claude Desktop",
                                "version": version,
                                "path": "Windows Package (winget)",
                                "extensions": []
                            }
                            
        except Exception as e:
            self.logger.debug(f"winget check failed: {e}", category="system")
        
        # Method 3: Check Windows Apps list
        try:
            self.logger.debug("Checking for Claude in Windows Apps", category="system")
            
            apps_cmd = [
                "powershell", "-Command",
                "Get-AppxPackage | Where-Object { $_.Name -like '*Claude*' } | Select-Object Name, Version | ConvertTo-Json"
            ]
            
            result = subprocess.run(
                apps_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    app_data = json.loads(result.stdout.strip())
                    if not isinstance(app_data, list):
                        app_data = [app_data]
                    
                    for app in app_data:
                        name = app.get('Name', '')
                        if 'claude' in name.lower():
                            version = app.get('Version', 'Unknown')
                            
                            self.logger.info(f"Claude found as Windows App: {name} v{version}", category="system")
                            
                            return {
                                "name": "Claude Desktop",
                                "version": version,
                                "path": "Windows Store App",
                                "extensions": []
                            }
                            
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Windows Apps check failed: {e}", category="system")
        
        return None
    
    def _check_windsurf(self) -> Optional[Dict]:
        """Check for Windsurf IDE installation"""
        if platform.system() == "Windows":
            # Check common Windsurf installation paths
            possible_paths = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Windsurf" / "Windsurf.exe",
                Path(os.environ.get("APPDATA", "")) / "Windsurf" / "Windsurf.exe",
                Path(os.environ.get("PROGRAMFILES", "")) / "Windsurf" / "Windsurf.exe",
                Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Windsurf" / "Windsurf.exe"
            ]
        else:
            # Linux/Mac paths for Windsurf
            possible_paths = [
                Path("/usr/bin/windsurf"),
                Path("/usr/local/bin/windsurf"),
                Path.home() / ".local" / "bin" / "windsurf",
                Path("/Applications/Windsurf.app/Contents/MacOS/Windsurf")  # Mac
            ]
        
        for path in possible_paths:
            if path.exists():
                # Avoid running Windsurf executable to prevent GUI opening
                version = "Installed"
                self.logger.info(f"Windsurf detected at {path} (avoiding executable)", category="system")
                
                return {
                    "name": "Windsurf",
                    "version": version,
                    "path": str(path),
                    "extensions": []
                }
        
        return None
    
    def _check_claude_code(self) -> Optional[Dict]:
        """Check for Claude Code CLI installation"""
        
        # Check if we're running in WSL first
        wsl_info = self._check_claude_code_in_wsl()
        if wsl_info:
            return wsl_info
        
        # On Windows, first try to find it via package management
        if platform.system() == "Windows":
            claude_code_info = self._find_claude_code_via_windows_packages()
            if claude_code_info:
                return claude_code_info
        
        # Try multiple possible command names for Claude Code
        claude_code_commands = ["claude-code", "claude_code", "claudecode", "cc"]
        
        for cmd in claude_code_commands:
            try:
                # Check if command is available
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.logger.info(f"Claude Code CLI detected via '{cmd}': {version}", category="system")
                    return {
                        "name": "Claude Code",
                        "version": version,
                        "path": f"CLI ({cmd})",
                        "extensions": []
                    }
            except Exception as e:
                self.logger.debug(f"Claude Code check with '{cmd}' failed: {e}", category="system")
        
        # Check for Claude Code installation files on Windows
        if platform.system() == "Windows":
            possible_paths = [
                # Check common installation paths
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Claude Code" / "claude-code.exe",
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ClaudeCode" / "claude-code.exe",
                Path(os.environ.get("APPDATA", "")) / "Claude Code" / "claude-code.exe",
                Path(os.environ.get("PROGRAMFILES", "")) / "Claude Code" / "claude-code.exe",
                
                # Check user directories
                Path(os.environ.get("USERPROFILE", "")) / ".claude-code" / "claude-code.exe",
                Path(os.environ.get("USERPROFILE", "")) / "claude-code" / "claude-code.exe",
                
                # Check if it's a portable installation
                Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "claude-code.exe",
                Path(os.environ.get("USERPROFILE", "")) / "Downloads" / "claude-code.exe"
            ]
            
            for path in possible_paths:
                if path.exists():
                    version = "Installed"
                    try:
                        # Try to get version without opening GUI
                        result = subprocess.run(
                            [str(path), "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        if result.returncode == 0:
                            version = result.stdout.strip()
                    except:
                        pass
                    
                    self.logger.info(f"Claude Code detected at {path}", category="system")
                    return {
                        "name": "Claude Code",
                        "version": version,
                        "path": str(path),
                        "extensions": []
                    }
        
        # Check if Claude Code might be installed via npm/node
        try:
            # Check if it's an npm global package
            result = subprocess.run(
                ["npm", "list", "-g", "claude-code"],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            if result.returncode == 0 and "claude-code" in result.stdout:
                # Extract version from npm list output
                import re
                version_match = re.search(r'claude-code@(\S+)', result.stdout)
                version = version_match.group(1) if version_match else "Unknown"
                
                self.logger.info(f"Claude Code detected via npm: {version}", category="system")
                return {
                    "name": "Claude Code",
                    "version": version,
                    "path": "NPM Global",
                    "extensions": []
                }
        except Exception as e:
            self.logger.debug(f"NPM Claude Code check failed: {e}", category="system")
        
        return None
    
    def _check_claude_code_in_wsl(self) -> Optional[Dict]:
        """Check for Claude Code installation in WSL environment"""
        try:
            # Check if we're running in WSL
            if not self._is_running_in_wsl():
                return None
            
            self.logger.debug("Detected WSL environment, checking for Claude Code", category="system")
            
            # WSL-specific Claude Code detection methods
            claude_code_commands = ["claude-code", "claude_code", "claudecode"]
            
            for cmd in claude_code_commands:
                try:
                    # Check if command is available in WSL
                    result = subprocess.run(
                        [cmd, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        self.logger.info(f"Claude Code detected in WSL via '{cmd}': {version}", category="system")
                        return {
                            "name": "Claude Code",
                            "version": version,
                            "path": f"WSL ({cmd})",
                            "extensions": [],
                            "environment": "WSL"
                        }
                except Exception as e:
                    self.logger.debug(f"WSL Claude Code check with '{cmd}' failed: {e}", category="system")
                    continue
            
            # Check for npm global installations in WSL
            try:
                result = subprocess.run(
                    ["npm", "list", "-g", "claude-code"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and "claude-code" in result.stdout:
                    # Extract version from npm list output
                    import re
                    version_match = re.search(r'claude-code@(\S+)', result.stdout)
                    version = version_match.group(1) if version_match else "Unknown"
                    
                    self.logger.info(f"Claude Code detected in WSL via npm: {version}", category="system")
                    return {
                        "name": "Claude Code",
                        "version": version,
                        "path": "WSL (NPM Global)",
                        "extensions": [],
                        "environment": "WSL"
                    }
            except Exception as e:
                self.logger.debug(f"WSL npm Claude Code check failed: {e}", category="system")
            
            # Check for Python pip installations in WSL
            try:
                pip_commands = ["pip", "pip3"]
                for pip_cmd in pip_commands:
                    result = subprocess.run(
                        [pip_cmd, "show", "claude-code"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        # Parse pip show output for version
                        version_line = next((line for line in result.stdout.split('\n') if line.startswith('Version:')), '')
                        version = version_line.split('Version: ')[-1].strip() if version_line else "Unknown"
                        
                        self.logger.info(f"Claude Code detected in WSL via {pip_cmd}: {version}", category="system")
                        return {
                            "name": "Claude Code",
                            "version": version,
                            "path": f"WSL (Python {pip_cmd})",
                            "extensions": [],
                            "environment": "WSL"
                        }
            except Exception as e:
                self.logger.debug(f"WSL pip Claude Code check failed: {e}", category="system")
            
            # Check common WSL installation paths
            wsl_paths = [
                Path.home() / ".local" / "bin" / "claude-code",
                Path("/usr/local/bin/claude-code"),
                Path("/usr/bin/claude-code"),
                Path.home() / "bin" / "claude-code"
            ]
            
            for path in wsl_paths:
                if path.exists():
                    try:
                        result = subprocess.run(
                            [str(path), "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        if result.returncode == 0:
                            version = result.stdout.strip()
                            self.logger.info(f"Claude Code detected in WSL at {path}: {version}", category="system")
                            return {
                                "name": "Claude Code",
                                "version": version,
                                "path": f"WSL ({path})",
                                "extensions": [],
                                "environment": "WSL"
                            }
                    except Exception as e:
                        self.logger.debug(f"Failed to check Claude Code at {path}: {e}", category="system")
            
            # Check for Windows installations accessible from WSL
            windows_claude_info = self._check_windows_claude_code_from_wsl()
            if windows_claude_info:
                return windows_claude_info
            
            return None
            
        except Exception as e:
            self.logger.debug(f"WSL Claude Code detection failed: {e}", category="system")
            return None
    
    def _is_running_in_wsl(self) -> bool:
        """Check if we're running in Windows Subsystem for Linux"""
        try:
            # Method 1: Check for WSL-specific environment variables
            if os.environ.get('WSL_DISTRO_NAME') or os.environ.get('WSLENV'):
                return True
            
            # Method 2: Check /proc/version for WSL signature
            try:
                with open('/proc/version', 'r') as f:
                    version_info = f.read().lower()
                    if 'microsoft' in version_info or 'wsl' in version_info:
                        return True
            except FileNotFoundError:
                pass
            
            # Method 3: Check /proc/sys/kernel/osrelease
            try:
                with open('/proc/sys/kernel/osrelease', 'r') as f:
                    osrelease = f.read().lower()
                    if 'microsoft' in osrelease or 'wsl' in osrelease:
                        return True
            except FileNotFoundError:
                pass
            
            # Method 4: Check if we can access Windows drives through WSL
            if platform.system() == "Linux":
                wsl_mount_points = ['/mnt/c', '/mnt/d', '/c', '/d']
                for mount_point in wsl_mount_points:
                    if Path(mount_point).exists():
                        return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"WSL detection failed: {e}", category="system")
            return False
    
    def _check_windows_claude_code_from_wsl(self) -> Optional[Dict]:
        """Check for Claude Code installed on Windows but accessible from WSL"""
        try:
            # Common Windows paths accessible through WSL mounts
            windows_paths = []
            
            # Check common Windows drive mounts
            for drive in ['c', 'd', 'e']:
                mount_base = Path(f"/mnt/{drive}")
                if mount_base.exists():
                    # Add common Windows installation paths
                    windows_paths.extend([
                        # User installations
                        mount_base / "Users" / os.environ.get('USER', 'user') / "AppData" / "Local" / "Programs" / "Claude Code" / "claude-code.exe",
                        mount_base / "Users" / os.environ.get('USER', 'user') / "AppData" / "Roaming" / "npm" / "claude-code.cmd",
                        mount_base / "Users" / os.environ.get('USER', 'user') / "AppData" / "Roaming" / "npm" / "claude-code",
                        
                        # System installations
                        mount_base / "Program Files" / "nodejs" / "claude-code.exe",
                        mount_base / "Program Files (x86)" / "nodejs" / "claude-code.exe",
                        mount_base / "nodejs" / "claude-code.exe",
                        
                        # Common npm global paths
                        mount_base / "Users" / os.environ.get('USER', 'user') / "AppData" / "Roaming" / "npm" / "node_modules" / "claude-code" / "bin" / "claude-code.js",
                        
                        # Windows PATH executable
                        mount_base / "Windows" / "System32" / "claude-code.exe"
                    ])
            
            for path in windows_paths:
                if path.exists():
                    try:
                        # Try to execute the Windows binary from WSL
                        result = subprocess.run(
                            [str(path), "--version"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        if result.returncode == 0:
                            version = result.stdout.strip()
                            self.logger.info(f"Claude Code detected on Windows (accessible from WSL) at {path}: {version}", category="system")
                            return {
                                "name": "Claude Code",
                                "version": version,
                                "path": f"Windows via WSL ({path})",
                                "extensions": [],
                                "environment": "Windows-WSL"
                            }
                    except Exception as e:
                        self.logger.debug(f"Failed to check Windows Claude Code at {path}: {e}", category="system")
                        continue
            
            # Try to use Windows PowerShell from WSL to detect Claude Code
            try:
                # Use powershell.exe to run Windows PowerShell from WSL
                ps_cmd = [
                    "powershell.exe", "-Command",
                    "Get-Command claude-code -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source"
                ]
                
                result = subprocess.run(
                    ps_cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    claude_code_path = result.stdout.strip()
                    
                    # Try to get version
                    version_cmd = ["powershell.exe", "-Command", "claude-code --version"]
                    version_result = subprocess.run(
                        version_cmd,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    version = version_result.stdout.strip() if version_result.returncode == 0 else "Unknown"
                    
                    self.logger.info(f"Claude Code detected via Windows PowerShell from WSL: {claude_code_path}", category="system")
                    return {
                        "name": "Claude Code",
                        "version": version,
                        "path": f"Windows PowerShell via WSL ({claude_code_path})",
                        "extensions": [],
                        "environment": "Windows-WSL"
                    }
                    
            except Exception as e:
                self.logger.debug(f"Windows PowerShell check from WSL failed: {e}", category="system")
            
            # Try using cmd.exe to find Claude Code
            try:
                cmd_result = subprocess.run(
                    ["cmd.exe", "/c", "where claude-code"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if cmd_result.returncode == 0 and cmd_result.stdout.strip():
                    claude_code_path = cmd_result.stdout.strip()
                    
                    # Try to get version
                    version_result = subprocess.run(
                        ["cmd.exe", "/c", "claude-code --version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    version = version_result.stdout.strip() if version_result.returncode == 0 else "Unknown"
                    
                    self.logger.info(f"Claude Code detected via Windows CMD from WSL: {claude_code_path}", category="system")
                    return {
                        "name": "Claude Code",
                        "version": version,
                        "path": f"Windows CMD via WSL ({claude_code_path})",
                        "extensions": [],
                        "environment": "Windows-WSL"
                    }
                    
            except Exception as e:
                self.logger.debug(f"Windows CMD check from WSL failed: {e}", category="system")
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Windows Claude Code check from WSL failed: {e}", category="system")
            return None
    
    def _find_claude_code_via_windows_packages(self) -> Optional[Dict]:
        """Find Claude Code using Windows package management"""
        try:
            # Method 1: Use PowerShell Get-Package to find Claude Code
            self.logger.debug("Checking for Claude Code via PowerShell Get-Package", category="system")
            
            ps_cmd = [
                "powershell", "-Command", 
                "Get-Package | Where-Object { $_.Name -like '*Claude*Code*' -or $_.Name -like '*ClaudeCode*' } | Select-Object Name, Version, Source, InstallLocation | ConvertTo-Json"
            ]
            
            result = subprocess.run(
                ps_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    package_data = json.loads(result.stdout.strip())
                    if not isinstance(package_data, list):
                        package_data = [package_data]
                    
                    for package in package_data:
                        name = package.get('Name', '')
                        if 'claude' in name.lower() and 'code' in name.lower():
                            version = package.get('Version', 'Unknown')
                            install_location = package.get('InstallLocation', 'Unknown')
                            source = package.get('Source', 'Unknown')
                            
                            self.logger.info(f"Claude Code found via Get-Package: {name} v{version}", category="system")
                            
                            return {
                                "name": "Claude Code",
                                "version": version,
                                "path": f"Windows Package ({source})",
                                "install_location": install_location,
                                "extensions": []
                            }
                            
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Could not parse Claude Code Get-Package JSON: {e}", category="system")
                    
        except Exception as e:
            self.logger.debug(f"Claude Code Get-Package check failed: {e}", category="system")
        
        # Method 2: Use winget to find Claude Code
        try:
            self.logger.debug("Checking for Claude Code via winget", category="system")
            
            winget_cmd = ["winget", "list", "claude-code"]
            
            result = subprocess.run(
                winget_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and "claude-code" in result.stdout.lower():
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'claude-code' in line.lower() and not line.startswith('-'):
                        parts = line.split()
                        if len(parts) >= 3:
                            name = parts[0]
                            version = parts[2] if len(parts) > 2 else "Unknown"
                            
                            self.logger.info(f"Claude Code found via winget: {name} v{version}", category="system")
                            
                            return {
                                "name": "Claude Code",
                                "version": version,
                                "path": "Windows Package (winget)",
                                "extensions": []
                            }
                            
        except Exception as e:
            self.logger.debug(f"Claude Code winget check failed: {e}", category="system")
        
        return None
    
    def _install_nodejs(self) -> Dict:
        """Attempt to install Node.js automatically"""
        self.logger.info("Attempting to install Node.js automatically", category="system")
        
        try:
            if platform.system() == "Windows":
                # Check if winget is available first
                winget_check = subprocess.run(
                    ["winget", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if winget_check.returncode != 0:
                    self.logger.warning("winget not available for Node.js installation", category="system")
                    return {
                        "status": False,
                        "message": "Cannot auto-install Node.js (winget not available)",
                        "details": "Please install manually from https://nodejs.org (version 18 or higher)"
                    }
                
                # Try using winget with more verbose output and better error handling
                self.logger.info("Installing Node.js via winget...", category="system")
                
                # Use different approaches for winget
                winget_commands = [
                    ["winget", "install", "OpenJS.NodeJS.LTS", "--silent", "--accept-package-agreements", "--accept-source-agreements"],
                    ["winget", "install", "OpenJS.NodeJS", "--silent", "--accept-package-agreements", "--accept-source-agreements"],
                    ["winget", "install", "nodejs", "--silent", "--accept-package-agreements", "--accept-source-agreements"]
                ]
                
                for cmd in winget_commands:
                    try:
                        self.logger.info(f"Trying: {' '.join(cmd)}", category="system")
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=600,  # 10 minutes timeout for installation
                            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                        )
                        
                        self.logger.info(f"Command output: {result.stdout}", category="system")
                        if result.stderr:
                            self.logger.warning(f"Command stderr: {result.stderr}", category="system")
                        
                        if result.returncode == 0:
                            # Wait a moment for installation to complete
                            import time
                            time.sleep(5)
                            
                            # Try to refresh PATH and test Node.js
                            self._refresh_environment_path()
                            
                            # Test if Node.js is now available
                            test_result = subprocess.run(
                                ["node", "--version"],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            
                            if test_result.returncode == 0:
                                version = test_result.stdout.strip()
                                self.logger.info(f"Node.js installed successfully: {version}", category="system")
                                return {
                                    "status": True,
                                    "message": f"Node.js installed successfully: {version}",
                                    "details": "Installed via Windows Package Manager (winget)"
                                }
                            else:
                                self.logger.warning("Node.js installation completed but not accessible", category="system")
                        else:
                            self.logger.warning(f"winget command failed with code {result.returncode}", category="system")
                            continue  # Try next command
                            
                    except subprocess.TimeoutExpired:
                        self.logger.warning(f"winget command timed out: {' '.join(cmd)}", category="system")
                        continue
                    except Exception as e:
                        self.logger.warning(f"winget command error: {e}", category="system")
                        continue
                
                # If all winget attempts failed
                self.logger.error("All winget installation attempts failed", category="system")
            
            # Fallback: Provide manual installation instructions
            return {
                "status": False,
                "message": "Node.js auto-installation failed",
                "details": "Please install manually: 1) Go to https://nodejs.org 2) Download LTS version 3) Run installer 4) Restart this application"
            }
            
        except Exception as e:
            self.logger.error("Node.js installation failed", e, category="system")
            return {
                "status": False,
                "message": f"Node.js installation failed: {str(e)}",
                "details": "Please install manually from https://nodejs.org"
            }
    
    def _refresh_environment_path(self):
        """Refresh the PATH environment variable on Windows"""
        if platform.system() == "Windows":
            try:
                # Get updated PATH from registry
                if WINDOWS_REGISTRY_AVAILABLE:
                    import winreg
                    
                    # Read machine PATH
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                      r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                        machine_path, _ = winreg.QueryValueEx(key, "PATH")
                    
                    # Read user PATH
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                        try:
                            user_path, _ = winreg.QueryValueEx(key, "PATH")
                        except FileNotFoundError:
                            user_path = ""
                    
                    # Update current process PATH
                    new_path = f"{machine_path};{user_path}"
                    os.environ["PATH"] = new_path
                    self.logger.info("Environment PATH refreshed", category="system")
                    
            except Exception as e:
                self.logger.warning(f"Failed to refresh PATH: {e}", category="system")
    
    def _install_winget(self) -> Dict:
        """Attempt to install winget automatically"""
        self.logger.info("Attempting to install winget automatically", category="system")
        
        return {
            "status": False,
            "message": "winget auto-installation not implemented",
            "details": "Please install from Microsoft Store: 'App Installer'"
        }
    
    def get_summary(self) -> Dict:
        """Get a summary of all check results"""
        if not self.results:
            return {"status": "not_run", "message": "System check not run yet"}
        
        passed = sum(1 for result in self.results.values() if result["status"])
        total = len(self.results)
        critical_failed = []
        
        # Define critical checks
        critical_checks = ["python", "platform", "internet", "node_js"]
        
        for check in critical_checks:
            if check in self.results and not self.results[check]["status"]:
                critical_failed.append(check)
        
        if critical_failed:
            return {
                "status": "failed",
                "message": f"Critical checks failed: {', '.join(critical_failed)}",
                "passed": passed,
                "total": total,
                "critical_failed": critical_failed
            }
        elif passed == total:
            return {
                "status": "passed",
                "message": "All system checks passed",
                "passed": passed,
                "total": total
            }
        else:
            return {
                "status": "partial",
                "message": f"{passed}/{total} checks passed",
                "passed": passed,
                "total": total
            }
    
    def format_results_for_display(self) -> str:
        """Format check results for display in GUI"""
        if not self.results:
            return "System check not run yet."
        
        output = []
        output.append("=== SYSTEM COMPATIBILITY CHECK ===\n")
        
        for check_name, result in self.results.items():
            status_icon = "[+]" if result["status"] else "[X]"
            status_text = "PASS" if result["status"] else "FAIL"
            
            output.append(f"{status_icon} {check_name.upper()}: {status_text}")
            output.append(f"   {result['message']}")
            if result.get("details"):
                output.append(f"   Details: {result['details']}")
            output.append("")
        
        # Add summary
        summary = self.get_summary()
        output.append("=== SUMMARY ===")
        output.append(f"Status: {summary['status'].upper()}")
        output.append(f"Message: {summary['message']}")
        
        if summary['status'] == 'failed':
            output.append("\n[!] Critical issues detected!")
            output.append("Please resolve the failed checks before proceeding.")
        elif summary['status'] == 'passed':
            output.append("\n[+] System is ready for MCP installation!")
        
        return "\n".join(output)
    
    def is_docker_available(self) -> bool:
        """Quick check if Docker is available and running"""
        try:
            docker_result = self.check_docker()
            return docker_result.get("status", False) and docker_result.get("daemon_running", False)
        except Exception:
            return False
    
    def get_docker_status(self) -> Dict:
        """Get detailed Docker status information"""
        if "docker" in self.results:
            return self.results["docker"]
        else:
            return self.check_docker()