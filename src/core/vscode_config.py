"""
VS Code extension configuration manager for MCP servers
Handles Cline and Roo extension MCP configurations
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import platform

from ..utils.logger import get_logger


class VSCodeExtensionConfig:
    """Manager for VS Code extension MCP configurations"""
    
    def __init__(self):
        self.logger = get_logger()
        
        # Extension configuration paths
        self.extension_configs = {
            "cline": {
                "name": "Cline",
                "id": "saoudrizwan.claude-dev",
                "config_path": self._get_cline_config_path(),
                "config_file": "cline_mcp_settings.json"
            },
            "roo": {
                "name": "Roo", 
                "id": "rooveterinaryinc.roo-cline",
                "config_path": self._get_roo_config_path(),
                "config_file": "mcp_settings.json"
            }
        }
    
    def _get_cline_config_path(self) -> str:
        """Get Cline extension MCP configuration path"""
        if platform.system() == "Windows":
            appdata = os.environ.get("APPDATA", "")
            return os.path.join(
                appdata, 
                "Code", 
                "User", 
                "globalStorage", 
                "saoudrizwan.claude-dev", 
                "settings"
            )
        else:
            # Linux/Mac paths
            home = Path.home()
            return str(home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings")
    
    def _get_roo_config_path(self) -> str:
        """Get Roo extension MCP configuration path"""
        if platform.system() == "Windows":
            appdata = os.environ.get("APPDATA", "")
            return os.path.join(
                appdata,
                "Code",
                "User", 
                "globalStorage",
                "rooveterinaryinc.roo-cline",
                "settings"
            )
        else:
            # Linux/Mac paths
            home = Path.home()
            return str(home / ".config" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings")
    
    def get_extension_config(self, extension: str) -> Optional[Dict]:
        """Read MCP configuration for a specific extension"""
        if extension not in self.extension_configs:
            self.logger.warning(f"Unknown extension: {extension}")
            return None
        
        ext_info = self.extension_configs[extension]
        config_dir = Path(ext_info["config_path"])
        config_file = config_dir / ext_info["config_file"]
        
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8-sig') as f:
                    config = json.load(f)
                
                self.logger.info(f"Loaded {ext_info['name']} MCP configuration", category="system")
                return config
            else:
                self.logger.info(f"{ext_info['name']} MCP configuration not found at {config_file}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to read {ext_info['name']} configuration", e)
            return None
    
    def update_extension_config(self, extension: str, mcp_servers: List[Dict]) -> bool:
        """Update MCP server configuration for an extension"""
        if extension not in self.extension_configs:
            self.logger.warning(f"Unknown extension: {extension}")
            return False
        
        ext_info = self.extension_configs[extension]
        config_dir = Path(ext_info["config_path"])
        config_file = config_dir / ext_info["config_file"]
        
        try:
            # Create directory if it doesn't exist
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing configuration or create new
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8-sig') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update MCP servers section
            if extension == "cline":
                config["mcpServers"] = self._format_servers_for_cline(mcp_servers)
            elif extension == "roo":
                config["mcpServers"] = self._format_servers_for_roo(mcp_servers)
            
            # Write updated configuration
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Updated {ext_info['name']} MCP configuration with {len(mcp_servers)} servers")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update {ext_info['name']} configuration", e)
            return False
    
    def _format_servers_for_cline(self, servers: List[Dict]) -> Dict:
        """Format server configurations for Cline extension"""
        formatted_servers = {}
        
        for server in servers:
            server_name = server.get("name", "unknown")
            server_config = {
                "command": server.get("command", ""),
                "args": server.get("args", []),
                "env": server.get("env", {})
            }
            
            formatted_servers[server_name] = server_config
        
        return formatted_servers
    
    def _format_servers_for_roo(self, servers: List[Dict]) -> Dict:
        """Format server configurations for Roo extension"""
        # Roo uses similar format to Cline
        return self._format_servers_for_cline(servers)
    
    def add_server_to_extension(self, extension: str, server_config: Dict) -> bool:
        """Add a single MCP server to an extension's configuration"""
        current_config = self.get_extension_config(extension)
        
        if current_config is None:
            current_config = {"mcpServers": {}}
        
        if "mcpServers" not in current_config:
            current_config["mcpServers"] = {}
        
        # Add the new server
        server_name = server_config.get("name", "unknown")
        
        if extension == "cline":
            current_config["mcpServers"][server_name] = {
                "command": server_config.get("command", ""),
                "args": server_config.get("args", []),
                "env": server_config.get("env", {})
            }
        elif extension == "roo":
            current_config["mcpServers"][server_name] = {
                "command": server_config.get("command", ""),
                "args": server_config.get("args", []),
                "env": server_config.get("env", {})
            }
        
        # Save the updated configuration
        return self._save_extension_config(extension, current_config)
    
    def remove_server_from_extension(self, extension: str, server_name: str) -> bool:
        """Remove a MCP server from an extension's configuration"""
        current_config = self.get_extension_config(extension)
        
        if current_config is None or "mcpServers" not in current_config:
            self.logger.warning(f"No MCP servers found in {extension} configuration")
            return False
        
        if server_name in current_config["mcpServers"]:
            del current_config["mcpServers"][server_name]
            self.logger.info(f"Removed server '{server_name}' from {extension}")
            return self._save_extension_config(extension, current_config)
        else:
            self.logger.warning(f"Server '{server_name}' not found in {extension} configuration")
            return False
    
    def _save_extension_config(self, extension: str, config: Dict) -> bool:
        """Save configuration to extension file"""
        if extension not in self.extension_configs:
            return False
        
        ext_info = self.extension_configs[extension]
        config_dir = Path(ext_info["config_path"])
        config_file = config_dir / ext_info["config_file"]
        
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save {ext_info['name']} configuration", e)
            return False
    
    def list_configured_servers(self, extension: str) -> List[str]:
        """List all configured MCP servers for an extension"""
        config = self.get_extension_config(extension)
        
        if config and "mcpServers" in config:
            return list(config["mcpServers"].keys())
        
        return []
    
    def get_extension_status(self) -> Dict[str, Dict]:
        """Get status of all supported extensions"""
        status = {}
        
        for ext_name, ext_info in self.extension_configs.items():
            config_dir = Path(ext_info["config_path"])
            config_file = config_dir / ext_info["config_file"]
            
            # Check if extension directory exists (indicates extension is installed)
            extension_installed = config_dir.parent.exists()
            
            # Check if MCP configuration exists
            config_exists = config_file.exists()
            
            # Count configured servers
            servers = self.list_configured_servers(ext_name)
            
            status[ext_name] = {
                "name": ext_info["name"],
                "installed": extension_installed,
                "config_exists": config_exists,
                "config_path": str(config_file),
                "server_count": len(servers),
                "servers": servers
            }
        
        return status
    
    def create_default_config(self, extension: str) -> bool:
        """Create a default MCP configuration for an extension"""
        default_config = {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", "C:\\"],
                    "env": {}
                }
            }
        }
        
        return self._save_extension_config(extension, default_config)