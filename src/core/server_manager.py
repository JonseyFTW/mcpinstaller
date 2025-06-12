"""
MCP Server Manager - handles discovery, installation, and management of MCP servers
"""

import json
import subprocess
import requests
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile
import platform

from ..utils.logger import get_logger
from .vscode_config import VSCodeExtensionConfig
from .system_checker import SystemChecker


class MCPServerManager:
    """Manages MCP server discovery, installation, and configuration"""
    
    def __init__(self):
        self.logger = get_logger()
        self.vscode_config = VSCodeExtensionConfig()
        self.system_checker = SystemChecker()
        
        # Load server definitions
        self.servers = self._load_server_definitions()
        
        # Discovery sources
        self.discovery_sources = [
            "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/servers.json",
            "https://api.github.com/search/repositories?q=mcp-server+in:name&sort=stars&order=desc",
            "https://registry.npmjs.org/-/v1/search?text=mcp-server&size=50"
        ]
    
    def _load_server_definitions(self) -> Dict:
        """Load server definitions from config file"""
        config_file = Path("config/servers.json")
        
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning("Server definitions file not found, using defaults")
                return self._get_default_servers()
                
        except Exception as e:
            self.logger.error("Failed to load server definitions", e)
            return self._get_default_servers()
    
    def _get_default_servers(self) -> Dict:
        """Return default server definitions"""
        return {
            "servers": {
                "filesystem": {
                    "name": "Filesystem MCP Server",
                    "description": "Provides secure file system operations",
                    "type": "npm",
                    "package": "@modelcontextprotocol/server-filesystem",
                    "category": "core",
                    "prerequisites": ["node"],
                    "configuration": {"args": ["C:\\"]},
                    "tags": ["file-operations", "essential"]
                },
                "git": {
                    "name": "Git MCP Server", 
                    "description": "Git repository operations",
                    "type": "npm",
                    "package": "@modelcontextprotocol/server-git",
                    "category": "development",
                    "prerequisites": ["node", "git"],
                    "configuration": {"args": ["."]},
                    "tags": ["git", "version-control"]
                }
            },
            "categories": {
                "core": {"name": "Core Services", "description": "Essential servers"},
                "development": {"name": "Development Tools", "description": "Dev tools"}
            }
        }
    
    def discover_servers(self) -> Dict[str, List[Dict]]:
        """Discover MCP servers from various sources"""
        self.logger.info("Starting MCP server discovery", category="install")
        
        discovered = {
            "local": list(self.servers.get("servers", {}).values()),
            "github": [],
            "npm": [],
            "official": []
        }
        
        # Discover from GitHub
        try:
            github_servers = self._discover_github_servers()
            discovered["github"] = github_servers
            self.logger.info(f"Found {len(github_servers)} servers on GitHub", category="install")
        except Exception as e:
            self.logger.error("GitHub discovery failed", e, category="install")
        
        # Discover from NPM
        try:
            npm_servers = self._discover_npm_servers()
            discovered["npm"] = npm_servers
            self.logger.info(f"Found {len(npm_servers)} servers on NPM", category="install")
        except Exception as e:
            self.logger.error("NPM discovery failed", e, category="install")
        
        # Discover from official sources
        try:
            official_servers = self._discover_official_servers()
            discovered["official"] = official_servers
            self.logger.info(f"Found {len(official_servers)} official servers", category="install")
        except Exception as e:
            self.logger.error("Official discovery failed", e, category="install")
        
        return discovered
    
    def _discover_github_servers(self) -> List[Dict]:
        """Discover MCP servers from GitHub"""
        servers = []
        
        try:
            response = requests.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": "mcp-server OR \"model context protocol\" server",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 20
                },
                timeout=8  # Reduced timeout to prevent hanging
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for repo in data.get("items", []):
                    server = {
                        "name": repo["name"],
                        "description": repo["description"] or "No description",
                        "type": "git",
                        "repository": repo["clone_url"],
                        "category": "community",
                        "stars": repo["stargazers_count"],
                        "language": repo["language"],
                        "source": "github"
                    }
                    servers.append(server)
            
        except Exception as e:
            self.logger.warning(f"GitHub API request failed: {e}")
        
        return servers
    
    def _discover_npm_servers(self) -> List[Dict]:
        """Discover MCP servers from NPM registry"""
        servers = []
        
        try:
            response = requests.get(
                "https://registry.npmjs.org/-/v1/search",
                params={
                    "text": "mcp-server OR @modelcontextprotocol",
                    "size": 30
                },
                timeout=8  # Reduced timeout to prevent hanging
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for package in data.get("objects", []):
                    pkg = package.get("package", {})
                    server = {
                        "name": pkg.get("name", "Unknown"),
                        "description": pkg.get("description", "No description"),
                        "type": "npm",
                        "package": pkg.get("name"),
                        "version": pkg.get("version"),
                        "category": "npm",
                        "source": "npm"
                    }
                    servers.append(server)
            
        except Exception as e:
            self.logger.warning(f"NPM registry request failed: {e}")
        
        return servers
    
    def _discover_official_servers(self) -> List[Dict]:
        """Discover servers from official MCP repository"""
        servers = []
        
        try:
            response = requests.get(
                "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md",
                timeout=8  # Reduced timeout to prevent hanging
            )
            
            if response.status_code == 200:
                # Parse the README for server information
                content = response.text
                
                # Simple parsing - look for NPM package references
                import re
                npm_packages = re.findall(r'@modelcontextprotocol/server-(\w+)', content)
                
                for package_name in set(npm_packages):
                    server = {
                        "name": f"{package_name.title()} MCP Server",
                        "description": f"Official {package_name} MCP server",
                        "type": "npm",
                        "package": f"@modelcontextprotocol/server-{package_name}",
                        "category": "official",
                        "source": "official"
                    }
                    servers.append(server)
            
        except Exception as e:
            self.logger.warning(f"Official repository request failed: {e}")
        
        return servers
    
    def install_server(self, server_config: Dict, target_path: Optional[str] = None) -> Tuple[bool, str]:
        """Install a MCP server based on its configuration"""
        server_name = server_config.get("name", "Unknown Server")
        server_type = server_config.get("type", "unknown")
        
        self.logger.log_server_operation("INSTALL", server_name, "Starting")
        
        try:
            if server_type == "npm":
                return self._install_npm_server(server_config, target_path)
            elif server_type == "git":
                return self._install_git_server(server_config, target_path)
            elif server_type == "python":
                return self._install_python_server(server_config, target_path)
            elif server_type == "docker":
                return self._install_docker_server(server_config)
            else:
                error_msg = f"Unsupported server type: {server_type}"
                self.logger.log_server_operation("INSTALL", server_name, f"Failed: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Installation failed: {str(e)}"
            self.logger.error(f"Server installation error for {server_name}", e, category="install")
            self.logger.log_server_operation("INSTALL", server_name, f"Failed: {error_msg}")
            return False, error_msg
    
    def _install_npm_server(self, server_config: Dict, target_path: Optional[str] = None) -> Tuple[bool, str]:
        """Install NPM-based MCP server"""
        package = server_config.get("package", "")
        server_name = server_config.get("name", package)
        
        if not package:
            return False, "No package specified"
        
        try:
            # Check if npm is available
            try:
                # On Windows, use shell=True for better PATH resolution
                if platform.system() == "Windows":
                    npm_check = subprocess.run(["npm", "--version"], capture_output=True, timeout=10, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    npm_check = subprocess.run(["npm", "--version"], capture_output=True, timeout=10)
                    
                if npm_check.returncode != 0:
                    self.logger.info(f"npm check failed with return code {npm_check.returncode}: {npm_check.stderr.decode()}", category="install")
                    return False, "npm is not available. Please install Node.js first."
                else:
                    npm_version = npm_check.stdout.decode().strip()
                    self.logger.info(f"Found npm version: {npm_version}", category="install")
            except FileNotFoundError as e:
                # Try to auto-install Node.js on Windows
                if platform.system() == "Windows":
                    self.logger.info(f"Node.js not found (FileNotFoundError: {str(e)}). Attempting auto-installation...", category="install")
                    nodejs_success = self._auto_install_nodejs()
                    if nodejs_success:
                        # Try npm check again after installation
                        try:
                            if platform.system() == "Windows":
                                npm_check = subprocess.run(["npm", "--version"], capture_output=True, timeout=10, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                            else:
                                npm_check = subprocess.run(["npm", "--version"], capture_output=True, timeout=10)
                            
                            if npm_check.returncode == 0:
                                npm_version = npm_check.stdout.decode().strip()
                                self.logger.info(f"Node.js installed successfully! npm version: {npm_version}", category="install")
                            else:
                                return False, "Node.js installed but npm still not working. Please restart the application."
                        except Exception as retry_error:
                            self.logger.error(f"npm check after installation failed: {str(retry_error)}", category="install")
                            return False, "Node.js installed but npm still not available. Please restart the application."
                    else:
                        return False, "Node.js/npm not found. Please install Node.js from https://nodejs.org/ and restart the application."
                else:
                    return False, "Node.js/npm not found. Please install Node.js from https://nodejs.org/ and restart the application."
            except Exception as e:
                return False, f"Cannot check npm availability: {str(e)}"
            
            # Install package globally
            self.logger.info(f"Installing NPM package: {package}", category="install")
            
            install_cmd = ["npm", "install", "-g", package]
            self.logger.info(f"Executing command: {' '.join(install_cmd)}", category="install")
            
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(
                        install_cmd,
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minutes
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    result = subprocess.run(
                        install_cmd,
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minutes
                    )
            except Exception as install_error:
                self.logger.error(f"NPM install subprocess failed: {str(install_error)}", category="install")
                return False, f"Installation error: {str(install_error)}"
            
            self.logger.log_command_execution(
                " ".join(install_cmd),
                result.returncode,
                result.stdout,
                result.stderr
            )
            
            if result.returncode == 0:
                success_msg = f"Successfully installed {server_name}"
                self.logger.info(f"NPM installation successful for {package}", category="install")
                self.logger.log_server_operation("INSTALL", server_name, "Success")
                
                # Try to configure in VS Code extensions
                self._configure_server_in_vscode(server_config)
                
                return True, success_msg
            else:
                self.logger.error(f"NPM install failed with return code {result.returncode}", category="install")
                self.logger.error(f"Command: {' '.join(install_cmd)}", category="install")
                self.logger.error(f"STDOUT: {result.stdout}", category="install")
                self.logger.error(f"STDERR: {result.stderr}", category="install")
                error_msg = f"npm install failed (exit code {result.returncode}): {result.stderr}"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Installation timed out"
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def _install_git_server(self, server_config: Dict, target_path: Optional[str] = None) -> Tuple[bool, str]:
        """Install Git-based MCP server"""
        repository = server_config.get("repository", "")
        server_name = server_config.get("name", "Git Server")
        
        if not repository:
            return False, "No repository URL specified"
        
        try:
            # Check if git is available
            if platform.system() == "Windows":
                git_check = subprocess.run(["git", "--version"], capture_output=True, timeout=10, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                git_check = subprocess.run(["git", "--version"], capture_output=True, timeout=10)
            if git_check.returncode != 0:
                return False, "git is not available. Please install Git first."
            
            # Determine target directory
            if not target_path:
                target_path = Path.home() / "mcp-servers" / server_name.replace(" ", "-").lower()
            else:
                target_path = Path(target_path)
            
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Clone repository
            self.logger.info(f"Cloning repository: {repository} to {target_path}", category="install")
            
            clone_cmd = ["git", "clone", repository, str(target_path)]
            if platform.system() == "Windows":
                result = subprocess.run(
                    clone_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    clone_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            
            self.logger.log_command_execution(
                " ".join(clone_cmd),
                result.returncode,
                result.stdout,
                result.stderr
            )
            
            if result.returncode == 0:
                # Check for package.json and install dependencies
                package_json = target_path / "package.json"
                if package_json.exists():
                    npm_install = subprocess.run(
                        ["npm", "install"],
                        cwd=target_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if npm_install.returncode != 0:
                        self.logger.warning(f"npm install failed in {target_path}")
                
                success_msg = f"Successfully cloned {server_name} to {target_path}"
                self.logger.log_server_operation("INSTALL", server_name, "Success")
                return True, success_msg
            else:
                error_msg = f"git clone failed: {result.stderr}"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Git clone timed out"
        except Exception as e:
            return False, f"Git installation error: {str(e)}"
    
    def _install_python_server(self, server_config: Dict, target_path: Optional[str] = None) -> Tuple[bool, str]:
        """Install Python-based MCP server"""
        package = server_config.get("package", "")
        repository = server_config.get("repository", "")
        server_name = server_config.get("name", "Python Server")
        
        try:
            # Check if python is available
            if platform.system() == "Windows":
                python_check = subprocess.run(["python", "--version"], capture_output=True, timeout=10, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                python_check = subprocess.run(["python", "--version"], capture_output=True, timeout=10)
            
            if python_check.returncode != 0:
                # Try python3
                if platform.system() == "Windows":
                    python_check = subprocess.run(["python3", "--version"], capture_output=True, timeout=10, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    python_check = subprocess.run(["python3", "--version"], capture_output=True, timeout=10)
                if python_check.returncode != 0:
                    return False, "Python is not available. Please install Python first."
                python_cmd = "python3"
            else:
                python_cmd = "python"
            
            if package:
                # Install from PyPI
                install_cmd = [python_cmd, "-m", "pip", "install", package]
                if platform.system() == "Windows":
                    result = subprocess.run(
                        install_cmd,
                        capture_output=True,
                        text=True,
                        timeout=300,
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    result = subprocess.run(
                        install_cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                
                if result.returncode == 0:
                    success_msg = f"Successfully installed Python package {package}"
                    self.logger.log_server_operation("INSTALL", server_name, "Success")
                    return True, success_msg
                else:
                    error_msg = f"pip install failed: {result.stderr}"
                    return False, error_msg
            
            elif repository:
                # Install from Git repository
                install_cmd = [python_cmd, "-m", "pip", "install", f"git+{repository}"]
                result = subprocess.run(
                    install_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    success_msg = f"Successfully installed Python server from {repository}"
                    self.logger.log_server_operation("INSTALL", server_name, "Success")
                    return True, success_msg
                else:
                    error_msg = f"pip install from git failed: {result.stderr}"
                    return False, error_msg
            
            else:
                return False, "No package or repository specified for Python server"
                
        except subprocess.TimeoutExpired:
            return False, "Python installation timed out"
        except Exception as e:
            return False, f"Python installation error: {str(e)}"
    
    def _install_docker_server(self, server_config: Dict) -> Tuple[bool, str]:
        """Install Docker-based MCP server with automatic Docker setup"""
        image = server_config.get("image", "")
        server_name = server_config.get("name", "Docker Server")
        
        if not image:
            return False, "No Docker image specified"
        
        # Check for fallback option if Docker fails
        fallback_config = server_config.get("fallback")
        
        try:
            return self._install_docker_server_impl(server_config)
        except Exception as docker_error:
            if fallback_config:
                self.logger.info(f"Docker installation failed for {server_name}, trying fallback method", category="install")
                return self._install_fallback_server(server_config, fallback_config)
            else:
                return False, f"Docker installation failed: {str(docker_error)}"
    
    def _install_docker_server_impl(self, server_config: Dict) -> Tuple[bool, str]:
        """Actual Docker server installation implementation"""
        image = server_config.get("image", "")
        server_name = server_config.get("name", "Docker Server")
        
        try:
            # Check Docker status
            docker_status = self.system_checker.get_docker_status()
            
            if not docker_status.get("status", False):
                # Docker not available - try to install/start it
                install_result = self._ensure_docker_available()
                if not install_result[0]:
                    return False, f"Docker setup failed: {install_result[1]}"
                
                # Re-check Docker after installation/start
                docker_status = self.system_checker.get_docker_status()
                if not docker_status.get("status", False):
                    return False, "Docker setup completed but Docker still not available"
            
            # Handle Docker image (pull or build automatically)
            if image.startswith("mcp-") and ":" in image:
                # Local image - build it automatically
                self.logger.info(f"Building local Docker image automatically: {image}", category="install")
                
                # Check if image already exists
                if self._docker_image_exists(image):
                    self.logger.info(f"Docker image {image} already exists, using existing image", category="install")
                    return self._run_docker_container(server_config, image)
                else:
                    self.logger.info(f"Docker image {image} not found, building automatically", category="install")
                    return self._build_and_run_docker_image(server_config, image)
            else:
                # Remote image - pull it
                self.logger.info(f"Pulling Docker image: {image}", category="install")
                
                pull_cmd = ["docker", "pull", image]
                if platform.system() == "Windows":
                    result = subprocess.run(
                        pull_cmd,
                        capture_output=True,
                        text=True,
                        timeout=600,  # 10 minutes for Docker pull
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    result = subprocess.run(
                        pull_cmd,
                        capture_output=True,
                        text=True,
                        timeout=600  # 10 minutes for Docker pull
                    )
            
            self.logger.log_command_execution(
                " ".join(pull_cmd),
                result.returncode,
                result.stdout,
                result.stderr
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully pulled Docker image: {image}", category="install")
                
                # After pulling, run the container automatically
                return self._run_docker_container(server_config, image)
            else:
                error_msg = f"docker pull failed: {result.stderr}"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Docker pull timed out"
        except Exception as e:
            return False, f"Docker installation error: {str(e)}"
    
    def _ensure_docker_available(self) -> Tuple[bool, str]:
        """Ensure Docker is installed and running"""
        try:
            docker_status = self.system_checker.get_docker_status()
            
            # Case 1: Docker not installed at all
            if not docker_status.get("installed", False) and docker_status.get("message", "").startswith("Docker not"):
                return self._install_docker()
            
            # Case 2: Docker installed but not running
            elif docker_status.get("installed", False) and not docker_status.get("daemon_running", False):
                return self._start_docker()
            
            # Case 3: Docker already available
            elif docker_status.get("status", False):
                return True, "Docker is already available"
            
            # Case 4: Unknown state
            else:
                return False, f"Unknown Docker state: {docker_status.get('message', 'Unknown')}"
                
        except Exception as e:
            return False, f"Failed to check Docker status: {str(e)}"
    
    def _install_docker(self) -> Tuple[bool, str]:
        """Install Docker automatically"""
        self.logger.info("Attempting to install Docker", category="install")
        
        try:
            if platform.system() == "Windows":
                # Try to install Docker Desktop via winget
                install_commands = [
                    ["winget", "install", "Docker.DockerDesktop", "--silent", "--accept-package-agreements", "--accept-source-agreements"],
                    ["winget", "install", "docker", "--silent", "--accept-package-agreements", "--accept-source-agreements"]
                ]
                
                for cmd in install_commands:
                    try:
                        self.logger.info(f"Trying Docker installation: {' '.join(cmd)}", category="install")
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=600,  # 10 minutes for installation
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        if result.returncode == 0:
                            self.logger.info("Docker installation completed via winget", category="install")
                            return True, "Docker Desktop installed successfully. Please restart the application to complete setup."
                        else:
                            self.logger.warning(f"winget Docker install failed: {result.stderr}", category="install")
                            continue
                            
                    except subprocess.TimeoutExpired:
                        self.logger.warning("Docker installation timed out", category="install")
                        continue
                    except Exception as e:
                        self.logger.warning(f"Docker installation attempt failed: {e}", category="install")
                        continue
                
                # If winget fails, provide manual instructions
                return False, "Automatic Docker installation failed. Please install Docker Desktop manually from https://docker.com/products/docker-desktop"
            
            else:
                # Non-Windows platforms
                return False, "Automatic Docker installation not supported on this platform. Please install Docker manually."
                
        except Exception as e:
            return False, f"Docker installation failed: {str(e)}"
    
    def _start_docker(self) -> Tuple[bool, str]:
        """Start Docker daemon/service"""
        self.logger.info("Attempting to start Docker", category="install")
        
        try:
            if platform.system() == "Windows":
                # Try to start Docker Desktop
                start_commands = [
                    ["powershell", "-Command", "Start-Process", "'Docker Desktop'"],
                    ["cmd", "/c", "start", "Docker Desktop"]
                ]
                
                for cmd in start_commands:
                    try:
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        if result.returncode == 0:
                            # Wait for Docker to start up
                            import time
                            self.logger.info("Waiting for Docker to start...", category="install")
                            time.sleep(10)
                            
                            # Check if Docker is now available
                            docker_status = self.system_checker.get_docker_status()
                            if docker_status.get("status", False):
                                return True, "Docker started successfully"
                            else:
                                return False, "Docker was started but is not yet ready. Please wait a moment and try again."
                        else:
                            continue
                            
                    except Exception as e:
                        self.logger.debug(f"Docker start attempt failed: {e}", category="install")
                        continue
                
                return False, "Could not start Docker automatically. Please start Docker Desktop manually."
            
            else:
                # Try systemctl on Linux
                try:
                    result = subprocess.run(
                        ["sudo", "systemctl", "start", "docker"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        return True, "Docker service started successfully"
                    else:
                        return False, f"Failed to start Docker service: {result.stderr}"
                        
                except Exception as e:
                    return False, f"Failed to start Docker on Linux: {str(e)}"
                    
        except Exception as e:
            return False, f"Failed to start Docker: {str(e)}"
    
    def _configure_server_in_vscode(self, server_config: Dict):
        """Configure installed server in VS Code extensions"""
        try:
            server_name = server_config.get("name", "Unknown")
            server_type = server_config.get("type", "")
            package = server_config.get("package", "")
            
            # Create configuration for VS Code extensions
            if server_type == "npm" and package:
                config = server_config.get("configuration", {})
                command = config.get("command", "npx")
                args = config.get("args", [package])
                
                # If args is empty or doesn't contain package, add it
                if not args or package not in args:
                    args = [package] + (args if args else [])
                
                vscode_config = {
                    "name": server_name,
                    "command": command,
                    "args": args,
                    "env": config.get("env", {})
                }
                
                # Try to add to Cline, Roo, and Claude Desktop if they exist
                for extension in ["cline", "roo", "claude_desktop"]:
                    try:
                        self.vscode_config.add_server_to_extension(extension, vscode_config)
                        extension_name = "Claude Desktop" if extension == "claude_desktop" else extension
                        self.logger.info(f"Added {server_name} to {extension_name} configuration")
                    except Exception as e:
                        extension_name = "Claude Desktop" if extension == "claude_desktop" else extension
                        self.logger.debug(f"Could not add to {extension_name}: {e}")
            
        except Exception as e:
            self.logger.warning(f"Failed to configure server in VS Code: {e}")
    
    def get_installed_servers(self) -> List[Dict]:
        """Get list of currently installed MCP servers"""
        installed = []
        
        # Check globally installed npm packages
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "--depth=0", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                dependencies = data.get("dependencies", {})
                
                for package_name, package_info in dependencies.items():
                    if "mcp" in package_name.lower() or "@modelcontextprotocol" in package_name:
                        installed.append({
                            "name": package_name,
                            "version": package_info.get("version", "unknown"),
                            "type": "npm",
                            "status": "installed"
                        })
        
        except Exception as e:
            self.logger.debug(f"Could not check npm packages: {e}")
        
        return installed
    
    def get_server_installation_status(self, server_config: Dict) -> Dict:
        """Check if a server is installed and configured in IDEs"""
        server_name = server_config.get("name", "Unknown")
        server_type = server_config.get("type", "")
        package = server_config.get("package", "")
        
        status = {
            "installed": False,
            "configured_in": [],
            "package_installed": False,
            "status": "not_installed"
        }
        
        try:
            # Check if package is installed
            if server_type == "npm" and package:
                installed_servers = self.get_installed_servers()
                for installed in installed_servers:
                    if installed["name"] == package:
                        status["package_installed"] = True
                        break
            
            # Check if configured in IDEs
            ide_status = self.vscode_config.get_extension_status()
            for ide_name, ide_info in ide_status.items():
                if ide_info["installed"]:
                    configured_servers = ide_info.get("servers", [])
                    
                    # Check if this server is in the IDE's configuration
                    for configured_server in configured_servers:
                        # Match by server name or package name
                        if (configured_server.lower().replace(" ", "_").replace("-", "_") == 
                            server_name.lower().replace(" ", "_").replace("-", "_")) or \
                           (package and package in configured_server):
                            status["configured_in"].append(ide_info["name"])
                            break
            
            # Determine overall status
            if status["package_installed"] and status["configured_in"]:
                status["installed"] = True
                status["status"] = "installed"
            elif status["package_installed"]:
                status["status"] = "installed_not_configured"
            elif status["configured_in"]:
                status["status"] = "configured_not_installed"
            else:
                status["status"] = "not_installed"
                
        except Exception as e:
            self.logger.debug(f"Could not check server status for {server_name}: {e}")
        
        return status
    
    def uninstall_server(self, server_config: Dict) -> Tuple[bool, str]:
        """Uninstall a MCP server"""
        server_name = server_config.get("name", "Unknown")
        server_type = server_config.get("type", "")
        
        self.logger.log_server_operation("UNINSTALL", server_name, "Starting")
        
        try:
            if server_type == "npm":
                package = server_config.get("package", "")
                if package:
                    result = subprocess.run(
                        ["npm", "uninstall", "-g", package],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        # Remove from VS Code configurations
                        for extension in ["cline", "roo"]:
                            self.vscode_config.remove_server_from_extension(extension, server_name)
                        
                        self.logger.log_server_operation("UNINSTALL", server_name, "Success")
                        return True, f"Successfully uninstalled {server_name}"
                    else:
                        return False, f"npm uninstall failed: {result.stderr}"
                
            # Add other uninstall methods for git, python, docker as needed
            
            return False, f"Uninstall not implemented for type: {server_type}"
            
        except Exception as e:
            error_msg = f"Uninstall failed: {str(e)}"
            self.logger.log_server_operation("UNINSTALL", server_name, f"Failed: {error_msg}")
            return False, error_msg
    
    def _auto_install_nodejs(self) -> bool:
        """Auto-install Node.js using winget on Windows"""
        try:
            self.logger.info("Attempting to install Node.js using winget...", category="install")
            
            # Try winget installation
            install_cmd = ["winget", "install", "OpenJS.NodeJS", "--accept-package-agreements", "--accept-source-agreements"]
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                self.logger.info("Node.js installation via winget successful", category="install")
                return True
            else:
                self.logger.error(f"Node.js installation failed: {result.stderr}", category="install")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Node.js installation timed out", category="install")
            return False
        except Exception as e:
            self.logger.error(f"Node.js auto-installation failed: {str(e)}", category="install")
            return False
    
    def _install_fallback_server(self, original_config: Dict, fallback_config: Dict) -> Tuple[bool, str]:
        """Install server using fallback configuration when primary method fails"""
        server_name = original_config.get("name", "Server")
        fallback_type = fallback_config.get("type", "unknown")
        
        try:
            self.logger.info(f"Installing {server_name} using fallback method: {fallback_type}", category="install")
            
            # Create temporary config with fallback settings
            temp_config = original_config.copy()
            temp_config.update(fallback_config)
            
            # Install using the fallback method
            if fallback_type == "npm":
                return self._install_npm_server(temp_config)
            elif fallback_type == "python":
                return self._install_python_server(temp_config)
            elif fallback_type == "git":
                return self._install_git_server(temp_config)
            else:
                return False, f"Unsupported fallback type: {fallback_type}"
                
        except Exception as e:
            return False, f"Fallback installation failed: {str(e)}"
    
    def _build_local_docker_image(self, server_config: Dict, image: str) -> Tuple[bool, str]:
        """Build local Docker image for MCP server"""
        server_name = server_config.get("name", "Server")
        
        try:
            # Determine Dockerfile based on image name
            image_name = image.split(":")[0]  # Remove tag
            dockerfile_map = {
                "mcp-filesystem": "Dockerfile.filesystem",
                "mcp-browser": "Dockerfile.playwright",
                "mcp-git": "Dockerfile.git",
                "mcp-memory": "Dockerfile.memory"
            }
            
            dockerfile = dockerfile_map.get(image_name)
            if not dockerfile:
                return False, f"No Dockerfile found for image: {image_name}"
            
            # Check if dockerfile exists
            dockerfile_path = Path("docker") / dockerfile
            if not dockerfile_path.exists():
                return False, f"Dockerfile not found: {dockerfile_path}"
            
            self.logger.info(f"Building Docker image {image} using {dockerfile}", category="install")
            
            # Build Docker image
            build_cmd = [
                "docker", "build",
                "-f", str(dockerfile_path),
                "-t", image,
                "docker"  # Build context
            ]
            
            if platform.system() == "Windows":
                result = subprocess.run(
                    build_cmd,
                    capture_output=True,
                    text=True,
                    timeout=1200,  # 20 minutes for Docker build
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    build_cmd,
                    capture_output=True,
                    text=True,
                    timeout=1200  # 20 minutes for Docker build
                )
            
            self.logger.log_command_execution(
                " ".join(build_cmd),
                result.returncode,
                result.stdout,
                result.stderr
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully built Docker image: {image}", category="install")
                
                # Add to IDE configurations
                self.vscode_config.add_server_to_extension("cline", server_config)
                self.vscode_config.add_server_to_extension("roo", server_config)
                
                self.logger.log_server_operation("INSTALL", server_name, "Success (Docker build)")
                return True, f"Successfully built and configured {server_name}"
            else:
                error_msg = f"Docker build failed: {result.stderr}"
                self.logger.log_server_operation("INSTALL", server_name, f"Failed: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            return False, "Docker build timed out"
        except Exception as e:
            return False, f"Docker build error: {str(e)}"
    
    def _docker_image_exists(self, image: str) -> bool:
        """Check if Docker image exists locally"""
        try:
            check_cmd = ["docker", "image", "inspect", image]
            result = subprocess.run(
                check_cmd,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            return result.returncode == 0
        except:
            return False
    
    def _build_and_run_docker_image(self, server_config: Dict, image: str) -> Tuple[bool, str]:
        """Build Docker image and run container automatically"""
        server_name = server_config.get("name", "Server")
        
        # First, build the image
        build_result = self._build_local_docker_image(server_config, image)
        if not build_result[0]:
            return build_result
        
        # Then run the container
        return self._run_docker_container(server_config, image)
    
    def _run_docker_container(self, server_config: Dict, image: str) -> Tuple[bool, str]:
        """Configure Docker-based MCP server for VS Code extensions"""
        server_name = server_config.get("name", "Server")
        
        try:
            self.logger.info(f"Configuring Docker MCP server: {server_name} using image: {image}", category="install")
            
            # Get configuration
            config = server_config.get("configuration", {})
            run_mode = config.get("run_mode", "daemon")
            
            # For MCP servers, configure VS Code to run them via Docker
            if run_mode == "interactive":
                # MCP servers run in stdio mode - configure VS Code to use docker run
                vscode_config = {
                    "name": server_name,
                    "command": "docker",
                    "args": [
                        "run", "-i", "--rm", "--init",
                        "--pull=always", image
                    ],
                    "env": config.get("environment", {})
                }
                
                self.logger.info(f"Configured {server_name} for stdio mode via Docker", category="install")
            else:
                # Traditional daemon container mode
                container_name = f"mcp-{server_name.lower().replace(' ', '-')}"
                ports = config.get("ports", [])
                volumes = config.get("volumes", [])
                environment = config.get("environment", {})
                
                # Build docker run command
                run_cmd = ["docker", "run", "-d", "--name", container_name]
                
                # Add port mappings
                for port in ports:
                    run_cmd.extend(["-p", port])
                
                # Add volume mappings
                for volume in volumes:
                    expanded_volume = self._expand_volume_path(volume)
                    run_cmd.extend(["-v", expanded_volume])
                
                # Add environment variables
                for key, value in environment.items():
                    run_cmd.extend(["-e", f"{key}={value}"])
                
                # Add restart policy
                run_cmd.extend(["--restart", "unless-stopped"])
                
                # Add image
                run_cmd.append(image)
                
                # Stop and remove existing container if it exists
                self._cleanup_existing_container(container_name)
                
                # Log the docker run command for debugging
                self.logger.info(f"Executing Docker run command: {' '.join(run_cmd)}", category="install")
                
                # Run the container
                if platform.system() == "Windows":
                    result = subprocess.run(
                        run_cmd,
                        capture_output=True,
                        text=True,
                        timeout=120,
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    result = subprocess.run(
                        run_cmd,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                
                self.logger.log_command_execution(
                    " ".join(run_cmd),
                    result.returncode,
                    result.stdout,
                    result.stderr
                )
                
                if result.returncode != 0:
                    error_msg = f"Docker run failed: {result.stderr}"
                    self.logger.log_server_operation("INSTALL", server_name, f"Failed: {error_msg}")
                    return False, error_msg
                
                container_id = result.stdout.strip()
                self.logger.info(f"Successfully started container: {container_name} ({container_id[:12]})", category="install")
                
                # Configure VS Code to connect to the running container
                vscode_config = {
                    "name": server_name,
                    "command": "docker",
                    "args": ["exec", "-i", container_name] + config.get("command", ["npx", "@playwright/mcp"]),
                    "env": environment
                }
            
            # Add to IDE configurations
            self.vscode_config.add_server_to_extension("cline", vscode_config)
            self.vscode_config.add_server_to_extension("roo", vscode_config)
            
            self.logger.log_server_operation("INSTALL", server_name, "Success (Docker MCP)")
            return True, f"Successfully configured {server_name} for MCP via Docker"
                
        except subprocess.TimeoutExpired:
            return False, "Docker container start timed out"
        except Exception as e:
            return False, f"Docker container error: {str(e)}"
    
    def _expand_volume_path(self, volume: str) -> str:
        """Expand environment variables and create directories in volume paths"""
        if "${MCP_WORKSPACE_PATH" in volume:
            # Default workspace path
            default_workspace = str(Path.home() / "mcp-workspace")
            workspace_path = os.environ.get("MCP_WORKSPACE_PATH", default_workspace)
            
            # Create directory if it doesn't exist
            Path(workspace_path).mkdir(parents=True, exist_ok=True)
            
            volume = volume.replace("${MCP_WORKSPACE_PATH:-./workspace}", workspace_path)
            volume = volume.replace("${MCP_WORKSPACE_PATH}", workspace_path)
        
        if "${MCP_DATA_PATH" in volume:
            # Default data path
            default_data = str(Path.home() / "mcp-data")
            data_path = os.environ.get("MCP_DATA_PATH", default_data)
            
            # Create directory if it doesn't exist
            Path(data_path).mkdir(parents=True, exist_ok=True)
            
            volume = volume.replace("${MCP_DATA_PATH:-./data}", data_path)
            volume = volume.replace("${MCP_DATA_PATH}", data_path)
        
        return volume
    
    def _cleanup_existing_container(self, container_name: str):
        """Stop and remove existing container if it exists"""
        try:
            # Stop container
            stop_cmd = ["docker", "stop", container_name]
            subprocess.run(
                stop_cmd,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            # Remove container
            rm_cmd = ["docker", "rm", container_name]
            subprocess.run(
                rm_cmd,
                capture_output=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            self.logger.info(f"Cleaned up existing container: {container_name}", category="install")
        except:
            pass  # Container might not exist, which is fine