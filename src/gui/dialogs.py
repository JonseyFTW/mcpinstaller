"""
Dialog windows for MCP Installer
Provides server discovery, installation, and configuration dialogs
"""

import customtkinter as ctk
import threading
import json
from typing import Dict, List, Optional, Callable
from pathlib import Path

from ..utils.logger import get_logger
from ..core.server_manager import MCPServerManager
from ..core.system_checker import SystemChecker


class ServerDiscoveryDialog:
    """Dialog for discovering and browsing available MCP servers"""
    
    def __init__(self, parent, callback: Optional[Callable] = None):
        self.parent = parent
        self.callback = callback
        self.logger = get_logger()
        self.server_manager = MCPServerManager()
        self.system_checker = SystemChecker()
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Discover MCP Servers")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Initialize discovered servers
        self.discovered_servers = {}
        self.selected_servers = []
        
        # Cache Docker status to avoid blocking UI
        self._docker_available = None
        self._cache_docker_status()
        
        # Create UI
        self._create_widgets()
        
        # Start with local-only discovery to avoid initial freeze
        self._load_local_only()
    
    def _cache_docker_status(self):
        """Cache Docker status in background to avoid UI blocking"""
        def check_docker():
            try:
                self._docker_available = self.system_checker.is_docker_available()
            except Exception as e:
                self.logger.debug(f"Docker status check failed: {e}")
                self._docker_available = False
        
        # Run Docker check in background thread
        threading.Thread(target=check_docker, daemon=True).start()
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (900 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (700 // 2)
        self.dialog.geometry(f"900x700+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self.dialog)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="[*] Discover MCP Servers",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Browse and install MCP servers from various sources",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Main content
        content_frame = ctk.CTkFrame(self.dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Source tabs
        self.tabview = ctk.CTkTabview(content_frame, width=850, height=500)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs for different sources
        self.local_tab = self.tabview.add("Local Catalog")
        self.official_tab = self.tabview.add("Official")
        self.github_tab = self.tabview.add("GitHub")
        self.npm_tab = self.tabview.add("NPM Registry")
        
        # Create server lists for each tab
        self._create_server_list(self.local_tab, "local")
        self._create_server_list(self.official_tab, "official")
        self._create_server_list(self.github_tab, "github")
        self._create_server_list(self.npm_tab, "npm")
        
        # Status and progress
        status_frame = ctk.CTkFrame(content_frame)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Starting discovery...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.pack(side="right", padx=20, pady=10)
        self.progress_bar.set(0)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="[R] Refresh All",
            width=120,
            command=self._start_discovery
        )
        self.refresh_btn.pack(side="left", padx=20, pady=15)
        
        self.local_only_btn = ctk.CTkButton(
            button_frame,
            text="[L] Load Local Only",
            width=140,
            command=self._load_local_only
        )
        self.local_only_btn.pack(side="left", padx=10, pady=15)
        
        self.install_btn = ctk.CTkButton(
            button_frame,
            text="[+] Install Selected",
            width=150,
            command=self._install_selected,
            state="disabled"
        )
        self.install_btn.pack(side="right", padx=(10, 20), pady=15)
        
        self.close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            width=100,
            command=self._close_dialog
        )
        self.close_btn.pack(side="right", padx=20, pady=15)
    
    def _create_server_list(self, parent, source: str):
        """Create scrollable server list for a tab"""
        
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(parent, width=800, height=400)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Store reference
        setattr(self, f"{source}_list", scrollable_frame)
        
        # Loading label
        loading_label = ctk.CTkLabel(
            scrollable_frame,
            text=f"Loading {source} servers...",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        loading_label.pack(pady=50)
        setattr(self, f"{source}_loading", loading_label)
    
    def _start_discovery(self):
        """Start server discovery in background thread"""
        self.status_label.configure(text="Discovering servers...")
        self.progress_bar.set(0.1)
        self.refresh_btn.configure(state="disabled")
        self.local_only_btn.configure(state="disabled")
        
        # Clear existing results
        self.discovered_servers = {}
        self.selected_servers = []
        self.install_btn.configure(state="disabled")
        
        # Start discovery thread
        threading.Thread(target=self._discover_servers, daemon=True).start()
    
    def _load_local_only(self):
        """Load only local servers quickly without network requests"""
        self.status_label.configure(text="Loading local servers...")
        self.progress_bar.set(0.1)
        self.refresh_btn.configure(state="disabled")
        self.local_only_btn.configure(state="disabled")
        
        try:
            # Load local servers immediately
            servers_dict = self.server_manager.servers.get("servers", {})
            self.logger.info(f"Loaded servers dict with {len(servers_dict)} entries: {list(servers_dict.keys())}", category="install")
            local_servers = list(servers_dict.values())
            self.logger.info(f"Converted to {len(local_servers)} server objects", category="install")
            
            # Clear other sources
            self.discovered_servers = {
                "local": local_servers,
                "github": [],
                "npm": [],
                "official": []
            }
            
            # Update progress
            self.progress_bar.set(0.5)
            
            # Populate only the local tab
            self._populate_single_list("local", local_servers)
            
            # Clear other tabs
            for source in ["github", "npm", "official"]:
                self._populate_single_list(source, [])
            
            # Complete
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Local servers loaded ({len(local_servers)} found)")
            self.refresh_btn.configure(state="normal")
            self.local_only_btn.configure(state="normal")
            
            self.logger.info(f"Local-only discovery completed: {len(local_servers)} servers", category="install")
            
        except Exception as e:
            self.logger.error("Local server loading failed", e)
            self._show_error(f"Failed to load local servers: {str(e)}")
            self.refresh_btn.configure(state="normal")
            self.local_only_btn.configure(state="normal")
    
    def _discover_servers(self):
        """Background thread for server discovery"""
        try:
            self.logger.log_user_action("Server discovery started")
            
            # Update progress
            self.dialog.after(0, lambda: self.progress_bar.set(0.2))
            self.dialog.after(0, lambda: self.status_label.configure(text="Loading local servers..."))
            
            # Initialize discovered servers
            discovered = {
                "local": [],
                "github": [],
                "npm": [],
                "official": []
            }
            
            # Load local servers first (fast)
            try:
                discovered["local"] = list(self.server_manager.servers.get("servers", {}).values())
                self.logger.info(f"Found {len(discovered['local'])} local servers", category="install")
                self.dialog.after(0, lambda: self.progress_bar.set(0.3))
                
                # Update local tab immediately
                self.dialog.after(0, lambda: self._populate_single_list("local", discovered["local"]))
                
            except Exception as e:
                self.logger.error("Local discovery failed", e, category="install")
            
            # Discover from online sources with progress updates
            online_sources = [
                ("official", "Loading official servers...", self.server_manager._discover_official_servers),
                ("github", "Loading GitHub servers...", self.server_manager._discover_github_servers),
                ("npm", "Loading NPM servers...", self.server_manager._discover_npm_servers)
            ]
            
            progress_step = 0.7 / len(online_sources)  # Remaining 70% divided by sources
            current_progress = 0.3
            
            for source_name, status_text, discover_func in online_sources:
                try:
                    # Update status
                    self.dialog.after(0, lambda t=status_text: self.status_label.configure(text=t))
                    
                    # Small delay to let UI process events
                    import time
                    time.sleep(0.1)
                    
                    # Discover servers
                    servers = discover_func()
                    discovered[source_name] = servers
                    self.logger.info(f"Found {len(servers)} servers from {source_name}", category="install")
                    
                    # Update progress
                    current_progress += progress_step
                    self.dialog.after(0, lambda p=current_progress: self.progress_bar.set(p))
                    
                    # Small delay before UI update
                    time.sleep(0.05)
                    
                    # Update this specific tab
                    self.dialog.after(0, lambda s=source_name, srv=servers: self._populate_single_list(s, srv))
                    
                    # Allow UI to process the updates
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"{source_name} discovery failed", e, category="install")
                    # Still update the tab to show "no servers found"
                    self.dialog.after(0, lambda s=source_name: self._populate_single_list(s, []))
            
            # Store final results
            self.discovered_servers = discovered
            
            # Final update
            self.dialog.after(0, self._discovery_completed)
            
        except Exception as e:
            self.logger.error("Server discovery failed", e)
            self.dialog.after(0, lambda: self._show_error(f"Discovery failed: {str(e)}"))
    
    def _populate_single_list(self, source: str, servers: List[Dict]):
        """Populate a single server list with discovered servers"""
        try:
            list_frame = getattr(self, f"{source}_list")
            loading_label = getattr(self, f"{source}_loading", None)
            
            # Remove loading label if it exists
            if loading_label and loading_label.winfo_exists():
                loading_label.destroy()
            
            # Clear existing content
            for widget in list_frame.winfo_children():
                widget.destroy()
            
            if not servers:
                no_servers_label = ctk.CTkLabel(
                    list_frame,
                    text=f"No servers found in {source}",
                    font=ctk.CTkFont(size=12),
                    text_color="gray60"
                )
                no_servers_label.pack(pady=20)
                return
            
            # Create server entries progressively to keep UI responsive
            self._create_server_entries_progressive(list_frame, servers, source, 0)
                
        except Exception as e:
            self.logger.error(f"Failed to populate {source} list", e)
    
    def _create_server_entries_progressive(self, list_frame, servers: List[Dict], source: str, index: int):
        """Create server entries progressively to maintain UI responsiveness"""
        if index >= len(servers):
            self.logger.info(f"Completed creating {index} server entries for {source}", category="install")
            return  # All entries created
        
        try:
            # Create one server entry
            server = servers[index]
            self.logger.debug(f"Creating server entry {index}: {server.get('name', 'Unknown')}", category="install")
            self._create_server_entry(list_frame, server, source, index)
            
            # Schedule next entry creation with a small delay to keep UI responsive
            # Process multiple entries per batch but with breaks
            batch_size = 3  # Create 3 entries per batch
            next_index = index + 1
            
            if next_index < len(servers):
                if (next_index % batch_size) == 0:
                    # After every batch, give UI thread a chance to process events
                    self.dialog.after(1, lambda: self._create_server_entries_progressive(list_frame, servers, source, next_index))
                else:
                    # Continue immediately within batch
                    self._create_server_entries_progressive(list_frame, servers, source, next_index)
                    
        except Exception as e:
            self.logger.error(f"Failed to create server entry {index} ({server.get('name', 'Unknown') if 'server' in locals() else 'N/A'})", e)
            # Continue with next server instead of stopping
            next_index = index + 1
            if next_index < len(servers):
                self.dialog.after(1, lambda: self._create_server_entries_progressive(list_frame, servers, source, next_index))
    
    def _discovery_completed(self):
        """Handle discovery completion"""
        self.status_label.configure(text="Discovery completed")
        self.progress_bar.set(1.0)
        self.refresh_btn.configure(state="normal")
        self.local_only_btn.configure(state="normal")
        self.logger.info("Server discovery completed successfully")
    
    def _update_server_lists(self):
        """Update server lists with discovered servers (legacy method)"""
        
        for source, servers in self.discovered_servers.items():
            self._populate_single_list(source, servers)
        
        self._discovery_completed()
    
    
    def _create_server_entry(self, parent, server: Dict, source: str, index: int):
        """Create a server entry widget with improved layout and install button"""
        
        try:
            # Check if this server requires Docker
            requires_docker = server.get('type', '') == 'docker'
            # Use cached Docker status to avoid blocking UI
            docker_available = self._docker_available if self._docker_available is not None else False
            
            # Main server frame - highlight if Docker is required but not available
            frame_color = "gray15" if requires_docker and not docker_available else None
            server_frame = ctk.CTkFrame(parent, fg_color=frame_color)
            server_frame.pack(fill="x", padx=5, pady=3)
            
            # Left section: Server info
            info_section = ctk.CTkFrame(server_frame, fg_color="transparent")
            info_section.pack(side="left", fill="x", expand=True, padx=15, pady=10)
            
            # Header row: Name, type, and status
            header_frame = ctk.CTkFrame(info_section, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 5))
            
            # Server name with Docker warning if needed
            name_text = server.get("name", "Unknown Server")
            if requires_docker and not docker_available:
                name_text += " [Docker Required]"
            
            name_color = "orange" if requires_docker and not docker_available else "white"
            name_label = ctk.CTkLabel(
                header_frame,
                text=name_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=name_color,
                anchor="w"
            )
            name_label.pack(side="left")
            
            # Server type badge with special color for Docker
            type_text = server.get('type', 'unknown').upper()
            if requires_docker:
                badge_color = "red" if not docker_available else "blue"
                badge_text = f"[{type_text} - DOCKER]"
            else:
                badge_color = "gray40"
                badge_text = f"[{type_text}]"
            
            type_label = ctk.CTkLabel(
                header_frame,
                text=badge_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="white",
                fg_color=badge_color,
                corner_radius=3,
                width=80 if requires_docker else 60,
                height=20
            )
            type_label.pack(side="left", padx=(10, 0))
            
            # Description with Docker warning if needed
            description = server.get("description", "No description available")
            if requires_docker and not docker_available:
                description += "\n⚠️ Docker is required but not running. Docker will be installed/started during installation."
            
            if len(description) > 120:
                description = description[:120] + "..."
            
            desc_color = "orange" if requires_docker and not docker_available else "gray70"
            desc_label = ctk.CTkLabel(
                info_section,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=desc_color,
                anchor="w",
                wraplength=500
            )
            desc_label.pack(fill="x", pady=(0, 5))
            
            # Details row
            details_frame = ctk.CTkFrame(info_section, fg_color="transparent")
            details_frame.pack(fill="x")
            
            details = []
            if "stars" in server and server["stars"] is not None:
                details.append(f"* {server['stars']}")
            if "version" in server and server["version"] is not None:
                details.append(f"v{server['version']}")
            if "language" in server and server["language"] is not None:
                details.append(str(server['language']))
            if "source" in server and server["source"] is not None:
                details.append(f"from {server['source']}")
            
            # Filter out None values and convert all to strings
            details = [str(detail) for detail in details if detail is not None and str(detail).strip()]
            
            if details:
                details_label = ctk.CTkLabel(
                    details_frame,
                    text=" • ".join(details),
                    font=ctk.CTkFont(size=10),
                    text_color="gray60",
                    anchor="w"
                )
                details_label.pack(side="left")
            
            # Right section: Actions
            action_section = ctk.CTkFrame(server_frame, fg_color="transparent")
            action_section.pack(side="right", padx=15, pady=10)
            
            # Check server installation status
            installation_status = self.server_manager.get_server_installation_status(server)
            
            # Determine button text and color based on installation status
            if installation_status["status"] == "installed":
                install_text = "✓ Installed"
                install_color = "green"
                install_hover = "dark green"
                button_width = 90
                is_installed = True
            elif installation_status["status"] == "installed_not_configured":
                install_text = "[⚠] Configure"
                install_color = "orange"
                install_hover = "dark orange"
                button_width = 90
                is_installed = False
            elif requires_docker and not docker_available:
                install_text = "[+] Install + Docker"
                install_color = "orange"
                install_hover = "dark orange"
                button_width = 120
                is_installed = False
            else:
                install_text = "[+] Install"
                install_color = None  # Default color
                install_hover = None  # Default hover
                button_width = 80
                is_installed = False
            
            # Create install button
            install_btn = ctk.CTkButton(
                action_section,
                text=install_text,
                width=button_width,
                height=32,
                font=ctk.CTkFont(size=11),
                fg_color=install_color,
                hover_color=install_hover,
                command=None  # Set command separately to avoid closure issues
            )
            
            # Define command function based on installation status
            if is_installed:
                # For installed servers, add a reinstall option
                def create_reinstall_command():
                    current_server = server.copy()
                    current_btn = install_btn
                    return lambda: self._reinstall_server_with_confirmation(current_server, current_btn)
                install_btn.configure(command=create_reinstall_command())
            else:
                # For not installed servers, use regular install
                def create_install_command():
                    current_server = server.copy()
                    current_btn = install_btn
                    return lambda: self._install_directly_with_button_feedback(current_server, current_btn)
                install_btn.configure(command=create_install_command())
            
            install_btn.pack(pady=2)
            
            # Add reinstall button for installed servers
            if is_installed:
                reinstall_btn = ctk.CTkButton(
                    action_section,
                    text="[↻] Reinstall",
                    width=80,
                    height=28,
                    font=ctk.CTkFont(size=10),
                    fg_color="gray50",
                    hover_color="gray40",
                    command=lambda s=server: self._reinstall_server_with_confirmation(s, None)
                )
                reinstall_btn.pack(pady=2)
            
            # Details button (for more info)
            details_btn = ctk.CTkButton(
                action_section,
                text="[i] Info",
                width=80,
                height=28,
                font=ctk.CTkFont(size=10),
                fg_color="gray50",
                hover_color="gray40",
                command=lambda s=server: self._show_server_details(s)
            )
            details_btn.pack(pady=2)
            
        except Exception as e:
            self.logger.error(f"Failed to create server entry {index}", e)
            # Create a simple error entry instead of failing completely
            error_frame = ctk.CTkFrame(parent)
            error_frame.pack(fill="x", padx=5, pady=3)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"Error loading server: {server.get('name', 'Unknown')} - {str(e)}",
                font=ctk.CTkFont(size=11),
                text_color="red"
            )
            error_label.pack(pady=10)
    
    def _on_server_selected(self, server: Dict, selected: bool):
        """Handle server selection"""
        if selected:
            if server not in self.selected_servers:
                self.selected_servers.append(server)
        else:
            if server in self.selected_servers:
                self.selected_servers.remove(server)
        
        # Update install button state
        self.install_btn.configure(state="normal" if self.selected_servers else "disabled")
    
    def _install_selected(self):
        """Install selected servers"""
        if not self.selected_servers:
            return
        
        # Create installation dialog
        InstallationDialog(self.dialog, self.selected_servers, self.server_manager)
    
    def _show_error(self, message: str):
        """Show error message"""
        self.status_label.configure(text=f"Error: {message}")
        self.progress_bar.set(0)
        self.refresh_btn.configure(state="normal")
        self.local_only_btn.configure(state="normal")
    
    def _install_single_server(self, server: Dict):
        """Install a single server directly"""
        try:
            server_name = server.get('name', 'Unknown')
            self.logger.log_user_action(f"Individual install requested: {server_name}")
            self.logger.info(f"Opening installation dialog for: {server_name}", category="install")
            
            # Show status update
            self.status_label.configure(text=f"Opening installer for {server_name}...")
            
            # Show installation progress dialog
            progress_dialog = SingleInstallDialog(self.dialog, server, self.server_manager)
            self.logger.info(f"Installation dialog created successfully for: {server_name}", category="install")
            self.logger.info(f"User must click '[>] Install Now' button to begin installation of: {server_name}", category="install")
            
            # Reset status
            self.status_label.configure(text="Ready")
            
        except Exception as e:
            self.logger.error("Failed to start individual installation", e)
            self.status_label.configure(text="Installation failed to start")
            self._show_error_popup(f"Failed to start installation: {str(e)}")
    
    def _install_directly_with_button_feedback(self, server: Dict, button):
        """Install server directly and update button to show progress"""
        server_name = server.get('name', 'Unknown')
        
        try:
            # Immediate button feedback
            button.configure(text="Installing...", state="disabled", fg_color="orange")
            self.status_label.configure(text=f"Installing {server_name}...")
            self.logger.log_user_action(f"Direct install started for: {server_name}")
            
            # Start installation in background thread
            def install_thread():
                try:
                    success, message = self.server_manager.install_server(server)
                    
                    # Update button based on result
                    if success:
                        self.dialog.after(0, lambda: button.configure(
                            text="✓ Installed", 
                            fg_color="green", 
                            state="disabled"
                        ))
                        self.dialog.after(0, lambda: self.status_label.configure(
                            text=f"✓ {server_name} installed successfully"
                        ))
                        self.logger.log_user_action(f"Installation successful: {server_name}")
                    else:
                        self.dialog.after(0, lambda: button.configure(
                            text="✗ Failed", 
                            fg_color="red", 
                            state="normal"
                        ))
                        self.dialog.after(0, lambda: self.status_label.configure(
                            text=f"✗ {server_name} installation failed: {message}"
                        ))
                        self.logger.error(f"Installation failed for {server_name}: {message}")
                        
                except Exception as e:
                    self.dialog.after(0, lambda: button.configure(
                        text="✗ Error", 
                        fg_color="red", 
                        state="normal"
                    ))
                    self.dialog.after(0, lambda: self.status_label.configure(
                        text=f"✗ {server_name} installation error"
                    ))
                    self.logger.error(f"Installation error for {server_name}", e)
            
            # Run installation in background
            threading.Thread(target=install_thread, daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Failed to start direct installation for {server_name}", e)
            button.configure(text="✗ Error", fg_color="red", state="normal")
            self.status_label.configure(text=f"✗ Failed to start installation")

    def _install_single_server_with_feedback(self, server: Dict, button=None):
        """Install server with immediate visual feedback and fallback option"""
        server_name = server.get('name', 'Unknown')
        
        try:
            # Immediate feedback
            self.status_label.configure(text=f"Starting installation of {server_name}...")
            self.logger.log_user_action(f"Install button clicked for: {server_name}")
            
            # Try to open dialog
            self._install_single_server(server)
            
        except Exception as dialog_error:
            self.logger.error(f"Dialog installation failed for {server_name}", dialog_error)
            
            # Fallback: Direct installation without dialog
            self._install_server_direct_fallback(server)
    
    def _install_server_direct_fallback(self, server: Dict):
        """Install server directly without dialog as fallback"""
        server_name = server.get('name', 'Unknown')
        
        try:
            self.logger.info(f"Using direct installation fallback for: {server_name}", category="install")
            self.status_label.configure(text=f"Installing {server_name} (direct mode)...")
            
            # Show confirmation dialog
            self._show_direct_install_confirmation(server)
            
        except Exception as e:
            self.logger.error(f"Direct installation fallback failed for {server_name}", e)
            self.status_label.configure(text="Installation failed")
            self._show_error_popup(f"Installation failed: {str(e)}")
    
    def _show_direct_install_confirmation(self, server: Dict):
        """Show confirmation dialog for direct installation"""
        server_name = server.get('name', 'Unknown')
        server_type = server.get('type', 'unknown')
        
        # Create simple confirmation dialog
        confirm_dialog = ctk.CTkToplevel(self.dialog)
        confirm_dialog.title("Confirm Installation")
        confirm_dialog.geometry("400x250")
        confirm_dialog.transient(self.dialog)
        confirm_dialog.grab_set()
        
        # Center the dialog
        confirm_dialog.update_idletasks()
        x = self.dialog.winfo_x() + (self.dialog.winfo_width() // 2) - (400 // 2)
        y = self.dialog.winfo_y() + (self.dialog.winfo_height() // 2) - (250 // 2)
        confirm_dialog.geometry(f"400x250+{x}+{y}")
        
        # Header
        ctk.CTkLabel(
            confirm_dialog,
            text="[+] Install MCP Server",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Info
        info_text = f"Install: {server_name}\nType: {server_type.upper()}"
        if 'package' in server:
            info_text += f"\nPackage: {server['package']}"
        
        ctk.CTkLabel(
            confirm_dialog,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(pady=10)
        
        # Status label for progress
        status_label = ctk.CTkLabel(
            confirm_dialog,
            text="Ready to install",
            font=ctk.CTkFont(size=11),
            text_color="gray70"
        )
        status_label.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def start_install():
            """Start installation process"""
            install_btn.configure(state="disabled", text="Installing...")
            cancel_btn.configure(state="disabled")
            status_label.configure(text="Installing...")
            
            def install_thread():
                try:
                    success, message = self.server_manager.install_server(server)
                    
                    confirm_dialog.after(0, lambda: installation_complete(success, message))
                    
                except Exception as e:
                    confirm_dialog.after(0, lambda: installation_complete(False, str(e)))
            
            threading.Thread(target=install_thread, daemon=True).start()
        
        def installation_complete(success, message):
            """Handle installation completion"""
            if success:
                status_label.configure(text="✓ Installation successful!", text_color="green")
                install_btn.configure(text="Done")
                self.status_label.configure(text=f"✓ {server_name} installed successfully")
            else:
                status_label.configure(text=f"✗ Installation failed: {message}", text_color="red")
                install_btn.configure(text="Failed")
                self.status_label.configure(text=f"✗ {server_name} installation failed")
            
            cancel_btn.configure(state="normal", text="Close")
            
            self.logger.log_user_action(f"Direct installation completed: {server_name} - {'Success' if success else 'Failed'}")
        
        install_btn = ctk.CTkButton(
            button_frame,
            text="Install Now",
            command=start_install,
            width=100
        )
        install_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=confirm_dialog.destroy,
            width=80,
            fg_color="gray40",
            hover_color="gray30"
        )
        cancel_btn.pack(side="right", padx=10)
    
    def _reinstall_server_with_confirmation(self, server: Dict, button):
        """Reinstall a server with confirmation dialog"""
        server_name = server.get('name', 'Unknown')
        
        # Create confirmation dialog
        confirm_dialog = ctk.CTkToplevel(self.dialog)
        confirm_dialog.title("Reinstall Server")
        confirm_dialog.geometry("400x250")
        confirm_dialog.transient(self.dialog)
        confirm_dialog.grab_set()
        
        # Center dialog
        confirm_dialog.update_idletasks()
        x = (confirm_dialog.winfo_screenwidth() - confirm_dialog.winfo_width()) // 2
        y = (confirm_dialog.winfo_screenheight() - confirm_dialog.winfo_height()) // 2
        confirm_dialog.geometry(f"+{x}+{y}")
        
        # Content
        message_label = ctk.CTkLabel(
            confirm_dialog,
            text=f"Reinstall {server_name}?",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        message_label.pack(pady=20)
        
        desc_label = ctk.CTkLabel(
            confirm_dialog,
            text="This will reinstall the server and update its configuration in all IDEs.",
            font=ctk.CTkFont(size=12),
            wraplength=350
        )
        desc_label.pack(pady=10)
        
        status_label = ctk.CTkLabel(
            confirm_dialog,
            text="Ready to reinstall",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        status_label.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def start_reinstall():
            status_label.configure(text="Reinstalling...", text_color="orange")
            reinstall_btn.configure(state="disabled")
            cancel_btn.configure(state="disabled")
            
            def reinstall_thread():
                try:
                    # Force reinstall by calling install_server
                    success, message = self.server_manager.install_server(server)
                    confirm_dialog.after(0, lambda: reinstall_complete(success, message))
                except Exception as e:
                    confirm_dialog.after(0, lambda: reinstall_complete(False, str(e)))
            
            threading.Thread(target=reinstall_thread, daemon=True).start()
        
        def reinstall_complete(success, message):
            if success:
                status_label.configure(text="✓ Reinstall successful!", text_color="green")
                reinstall_btn.configure(text="Done")
                self.status_label.configure(text=f"✓ {server_name} reinstalled successfully")
                # Refresh the server list to update button states
                self._load_local_only()
            else:
                status_label.configure(text=f"✗ Reinstall failed: {message}", text_color="red")
                reinstall_btn.configure(text="Failed")
                self.status_label.configure(text=f"✗ {server_name} reinstall failed")
        
        reinstall_btn = ctk.CTkButton(
            button_frame,
            text="[↻] Reinstall",
            command=start_reinstall,
            width=100,
            fg_color="orange",
            hover_color="dark orange"
        )
        reinstall_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=confirm_dialog.destroy,
            width=80,
            fg_color="gray40",
            hover_color="gray30"
        )
        cancel_btn.pack(side="right", padx=10)
    
    def _show_server_details(self, server: Dict):
        """Show detailed information about a server"""
        try:
            details_dialog = ServerDetailsDialog(self.dialog, server)
            
        except Exception as e:
            self.logger.error("Failed to show server details", e)
            self._show_error_popup(f"Failed to show details: {str(e)}")
    
    def _show_error_popup(self, message: str):
        """Show a simple error popup"""
        error_dialog = ctk.CTkToplevel(self.dialog)
        error_dialog.title("Error")
        error_dialog.geometry("400x150")
        error_dialog.transient(self.dialog)
        error_dialog.grab_set()
        
        # Center the popup
        error_dialog.update_idletasks()
        x = self.dialog.winfo_x() + (self.dialog.winfo_width() // 2) - (400 // 2)
        y = self.dialog.winfo_y() + (self.dialog.winfo_height() // 2) - (150 // 2)
        error_dialog.geometry(f"400x150+{x}+{y}")
        
        ctk.CTkLabel(
            error_dialog, 
            text="[X] Error", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            error_dialog, 
            text=message, 
            wraplength=350,
            font=ctk.CTkFont(size=11)
        ).pack(pady=10)
        
        ctk.CTkButton(
            error_dialog, 
            text="OK", 
            command=error_dialog.destroy
        ).pack(pady=20)
    
    def _close_dialog(self):
        """Close the dialog"""
        if self.callback:
            self.callback(self.selected_servers)
        self.dialog.destroy()


class InstallationDialog:
    """Dialog for installing selected MCP servers"""
    
    def __init__(self, parent, servers: List[Dict], server_manager: MCPServerManager):
        self.parent = parent
        self.servers = servers
        self.server_manager = server_manager
        self.logger = get_logger()
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Install MCP Servers")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Installation state
        self.current_index = 0
        self.results = []
        self.installing = False
        
        # Create UI
        self._create_widgets()
    
    def _center_dialog(self):
        """Center dialog on parent"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (600 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
    
    def _create_widgets(self):
        """Create installation dialog widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self.dialog)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="[+] Install MCP Servers",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)
        
        count_label = ctk.CTkLabel(
            header_frame,
            text=f"Installing {len(self.servers)} server(s)",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        count_label.pack(pady=(0, 15))
        
        # Progress section
        progress_frame = ctk.CTkFrame(self.dialog)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.overall_progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to install",
            font=ctk.CTkFont(size=12)
        )
        self.overall_progress_label.pack(pady=(15, 5))
        
        self.overall_progress = ctk.CTkProgressBar(progress_frame, width=400)
        self.overall_progress.pack(pady=(0, 15))
        self.overall_progress.set(0)
        
        # Current server info
        self.current_server_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.current_server_label.pack(pady=(0, 15))
        
        # Results area
        results_frame = ctk.CTkFrame(self.dialog)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        results_label = ctk.CTkLabel(
            results_frame,
            text="Installation Results",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        results_label.pack(pady=(15, 5))
        
        self.results_text = ctk.CTkTextbox(
            results_frame,
            width=550,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.results_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.start_btn = ctk.CTkButton(
            button_frame,
            text="[>] Start Installation",
            width=150,
            command=self._start_installation
        )
        self.start_btn.pack(side="left", padx=20, pady=15)
        
        self.close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            width=100,
            command=self._close_dialog,
            state="disabled"
        )
        self.close_btn.pack(side="right", padx=20, pady=15)
    
    def _start_installation(self):
        """Start the installation process"""
        self.installing = True
        self.start_btn.configure(state="disabled")
        self.results_text.delete("0.0", "end")
        
        self._add_result("Starting installation process...\n")
        
        # Start installation in background thread
        threading.Thread(target=self._install_servers, daemon=True).start()
    
    def _install_servers(self):
        """Install servers in background thread"""
        try:
            total_servers = len(self.servers)
            
            for i, server in enumerate(self.servers):
                self.current_index = i
                
                # Update UI
                self.dialog.after(0, lambda s=server, idx=i: self._update_progress(s, idx))
                
                # Install server
                server_name = server.get("name", "Unknown Server")
                self._add_result(f"\n[{i+1}/{total_servers}] Installing {server_name}...")
                
                success, message = self.server_manager.install_server(server)
                
                # Record result
                result = {
                    "server": server,
                    "success": success,
                    "message": message
                }
                self.results.append(result)
                
                # Update UI
                if success:
                    self._add_result(f"[+] Success: {message}")
                else:
                    self._add_result(f"[X] Failed: {message}")
            
            # Installation complete
            self.dialog.after(0, self._installation_complete)
            
        except Exception as e:
            self.logger.error("Installation process failed", e)
            self.dialog.after(0, lambda: self._add_result(f"\n✗ Installation process failed: {str(e)}"))
            self.dialog.after(0, self._installation_complete)
    
    def _update_progress(self, server: Dict, index: int):
        """Update progress indicators"""
        total = len(self.servers)
        progress = (index + 1) / total
        
        self.overall_progress.set(progress)
        self.overall_progress_label.configure(
            text=f"Installing {index + 1} of {total} servers"
        )
        
        server_name = server.get("name", "Unknown Server")
        server_type = server.get("type", "unknown")
        self.current_server_label.configure(
            text=f"Current: {server_name} ({server_type})"
        )
    
    def _add_result(self, text: str):
        """Add text to results area"""
        def add_text():
            self.results_text.insert("end", text + "\n")
            self.results_text.see("end")
        
        if threading.current_thread() == threading.main_thread():
            add_text()
        else:
            self.dialog.after(0, add_text)
    
    def _installation_complete(self):
        """Handle installation completion"""
        self.installing = False
        
        # Update progress
        self.overall_progress.set(1.0)
        self.overall_progress_label.configure(text="Installation completed")
        self.current_server_label.configure(text="")
        
        # Show summary
        successful = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - successful
        
        self._add_result(f"\n{'='*50}")
        self._add_result(f"INSTALLATION SUMMARY")
        self._add_result(f"{'='*50}")
        self._add_result(f"Successful: {successful}")
        self._add_result(f"Failed: {failed}")
        self._add_result(f"Total: {len(self.results)}")
        
        if failed > 0:
            self._add_result(f"\nFailed installations:")
            for result in self.results:
                if not result["success"]:
                    server_name = result["server"].get("name", "Unknown")
                    self._add_result(f"  - {server_name}: {result['message']}")
        
        # Enable close button
        self.close_btn.configure(state="normal")
        
        self.logger.log_user_action(f"Installation completed: {successful} successful, {failed} failed")
    
    def _close_dialog(self):
        """Close the dialog"""
        if not self.installing:
            self.dialog.destroy()


class SingleInstallDialog:
    """Dialog for installing a single MCP server"""
    
    def __init__(self, parent, server: Dict, server_manager):
        try:
            self.parent = parent
            self.server = server
            self.server_manager = server_manager
            self.logger = get_logger()
            
            server_name = server.get('name', 'Server')
            self.logger.info(f"Initializing installation dialog for: {server_name}", category="install")
            
            # Create dialog
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(f"Install {server_name}")
            self.dialog.geometry("500x400")
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            self.logger.info(f"Dialog window created for: {server_name}", category="install")
            
            # Center dialog
            self._center_dialog()
            
            # Installation state
            self.installing = False
            self.success = False
            
            # Create UI
            self._create_widgets()
            
            self.logger.info(f"Installation dialog fully initialized for: {server_name}", category="install")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SingleInstallDialog", e)
            raise
    
    def _center_dialog(self):
        """Center dialog on parent"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (500 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
    
    def _create_widgets(self):
        """Create installation dialog widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self.dialog)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"[+] Install {self.server.get('name', 'Server')}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=15)
        
        # Server info
        info_frame = ctk.CTkFrame(self.dialog)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_text = f"Type: {self.server.get('type', 'unknown').upper()}\n"
        if 'package' in self.server:
            info_text += f"Package: {self.server['package']}\n"
        if 'repository' in self.server:
            info_text += f"Repository: {self.server['repository']}\n"
        if 'version' in self.server:
            info_text += f"Version: {self.server['version']}\n"
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text.strip(),
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left"
        )
        info_label.pack(pady=15, padx=15)
        
        # Progress section
        progress_frame = ctk.CTkFrame(self.dialog)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to install - Click '[>] Install Now' to begin",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(15, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_bar.pack(pady=(0, 15))
        self.progress_bar.set(0)
        
        # Output area
        output_frame = ctk.CTkFrame(self.dialog)
        output_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Installation Output",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        output_label.pack(pady=(15, 5))
        
        self.output_text = ctk.CTkTextbox(
            output_frame,
            width=450,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.install_btn = ctk.CTkButton(
            button_frame,
            text="[>] Install Now",
            width=120,
            command=self._start_installation
        )
        self.install_btn.pack(side="left", padx=20, pady=15)
        
        self.close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            width=80,
            command=self._close_dialog,
            state="disabled"
        )
        self.close_btn.pack(side="right", padx=20, pady=15)
    
    def _start_installation(self):
        """Start the installation process"""
        self.installing = True
        self.install_btn.configure(state="disabled")
        self.output_text.delete("0.0", "end")
        
        self._add_output("Starting installation...\n")
        self.status_label.configure(text="Installing...")
        self.progress_bar.set(0.1)
        
        # Start installation in background thread
        threading.Thread(target=self._install_server, daemon=True).start()
    
    def _install_server(self):
        """Install server in background thread"""
        try:
            server_name = self.server.get("name", "Unknown Server")
            self._add_output(f"Installing {server_name}...\n")
            
            # Update progress
            self.dialog.after(0, lambda: self.progress_bar.set(0.3))
            
            # Install server
            success, message = self.server_manager.install_server(self.server)
            
            # Update UI
            self.dialog.after(0, lambda: self._installation_complete(success, message))
            
        except Exception as e:
            self.logger.error("Single server installation failed", e)
            self.dialog.after(0, lambda: self._installation_complete(False, f"Installation failed: {str(e)}"))
    
    def _installation_complete(self, success: bool, message: str):
        """Handle installation completion"""
        self.installing = False
        self.success = success
        
        # Update progress
        self.progress_bar.set(1.0)
        
        if success:
            self.status_label.configure(text="[+] Installation successful!")
            self._add_output(f"\n[+] SUCCESS: {message}\n")
            self._add_output("\nServer has been installed and configured in VS Code extensions.\n")
        else:
            self.status_label.configure(text="[X] Installation failed")
            self._add_output(f"\n[X] FAILED: {message}\n")
        
        # Enable close button
        self.close_btn.configure(state="normal")
        
        self.logger.log_user_action(f"Single installation completed: {self.server.get('name')} - {'Success' if success else 'Failed'}")
    
    def _add_output(self, text: str):
        """Add text to output area"""
        def add_text():
            self.output_text.insert("end", text)
            self.output_text.see("end")
        
        if threading.current_thread() == threading.main_thread():
            add_text()
        else:
            self.dialog.after(0, add_text)
    
    def _close_dialog(self):
        """Close the dialog"""
        if not self.installing:
            self.dialog.destroy()


class ServerDetailsDialog:
    """Dialog showing detailed information about a server"""
    
    def __init__(self, parent, server: Dict):
        self.parent = parent
        self.server = server
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Server Details: {server.get('name', 'Unknown')}")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Create UI
        self._create_widgets()
    
    def _center_dialog(self):
        """Center dialog on parent"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (600 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
    
    def _create_widgets(self):
        """Create details dialog widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self.dialog)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"[i] {self.server.get('name', 'Unknown Server')}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)
        
        # Details area
        details_frame = ctk.CTkScrollableFrame(self.dialog, width=550, height=350)
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Build details text
        details_text = self._build_details_text()
        
        details_label = ctk.CTkLabel(
            details_frame,
            text=details_text,
            font=ctk.CTkFont(size=11),
            anchor="nw",
            justify="left"
        )
        details_label.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Close button
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            width=100,
            command=self.dialog.destroy
        )
        close_btn.pack(pady=15)
    
    def _build_details_text(self) -> str:
        """Build detailed information text"""
        details = []
        
        # Basic info
        details.append("=== BASIC INFORMATION ===")
        details.append(f"Name: {self.server.get('name', 'Unknown')}")
        details.append(f"Type: {self.server.get('type', 'unknown').upper()}")
        details.append(f"Category: {self.server.get('category', 'unknown')}")
        
        if 'description' in self.server:
            details.append(f"Description: {self.server['description']}")
        
        details.append("")
        
        # Technical details
        details.append("=== TECHNICAL DETAILS ===")
        if 'package' in self.server:
            details.append(f"Package: {self.server['package']}")
        if 'repository' in self.server:
            details.append(f"Repository: {self.server['repository']}")
        if 'image' in self.server:
            details.append(f"Docker Image: {self.server['image']}")
        if 'version' in self.server:
            details.append(f"Version: {self.server['version']}")
        if 'language' in self.server:
            details.append(f"Language: {self.server['language']}")
        
        details.append("")
        
        # Source info
        details.append("=== SOURCE INFORMATION ===")
        if 'source' in self.server:
            details.append(f"Source: {self.server['source']}")
        if 'stars' in self.server:
            details.append(f"GitHub Stars: {self.server['stars']}")
        
        details.append("")
        
        # Prerequisites
        if 'prerequisites' in self.server:
            details.append("=== PREREQUISITES ===")
            prereqs = self.server['prerequisites']
            if isinstance(prereqs, list):
                for prereq in prereqs:
                    details.append(f"- {prereq}")
            else:
                details.append(f"- {prereqs}")
            details.append("")
        
        # Configuration
        if 'configuration' in self.server:
            config = self.server['configuration']
            details.append("=== CONFIGURATION ===")
            
            if 'command' in config:
                details.append(f"Command: {config['command']}")
            if 'args' in config and config['args']:
                details.append(f"Arguments: {' '.join(config['args'])}")
            if 'env' in config and config['env']:
                details.append("Environment Variables:")
                for key, value in config['env'].items():
                    details.append(f"  {key}={value}")
            
            details.append("")
        
        # Tags
        if 'tags' in self.server:
            details.append("=== TAGS ===")
            tags = self.server['tags']
            if isinstance(tags, list):
                details.append(", ".join(tags))
            else:
                details.append(str(tags))
        
        return "\n".join(details)


class ServerCreationDialog:
    """Dialog for creating custom MCP server configurations"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = get_logger()
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Create Custom MCP Server")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Create UI
        self._create_widgets()
    
    def _center_dialog(self):
        """Center dialog on parent"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (700 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (600 // 2)
        self.dialog.geometry(f"700x600+{x}+{y}")
    
    def _create_widgets(self):
        """Create server creation dialog widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self.dialog)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="[+] Create Custom MCP Server",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)
        
        # Form
        form_frame = ctk.CTkScrollableFrame(self.dialog, width=650, height=400)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Server Name
        ctk.CTkLabel(form_frame, text="Server Name:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.name_entry = ctk.CTkEntry(form_frame, width=400, placeholder_text="My Custom Server")
        self.name_entry.pack(anchor="w", pady=(0, 10))
        
        # Server Type
        ctk.CTkLabel(form_frame, text="Server Type:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.type_combo = ctk.CTkComboBox(form_frame, values=["npm", "python", "git", "docker"], width=200)
        self.type_combo.pack(anchor="w", pady=(0, 10))
        self.type_combo.set("npm")
        
        # Description
        ctk.CTkLabel(form_frame, text="Description:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.description_text = ctk.CTkTextbox(form_frame, width=600, height=80)
        self.description_text.pack(anchor="w", pady=(0, 10))
        
        # Package/Repository
        ctk.CTkLabel(form_frame, text="Package/Repository:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.package_entry = ctk.CTkEntry(form_frame, width=400, placeholder_text="npm package name or git repository URL")
        self.package_entry.pack(anchor="w", pady=(0, 10))
        
        # Command and Args
        ctk.CTkLabel(form_frame, text="Command:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.command_entry = ctk.CTkEntry(form_frame, width=400, placeholder_text="npx")
        self.command_entry.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Arguments (one per line):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.args_text = ctk.CTkTextbox(form_frame, width=600, height=80)
        self.args_text.pack(anchor="w", pady=(0, 10))
        
        # Environment Variables
        ctk.CTkLabel(form_frame, text="Environment Variables (KEY=value, one per line):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.env_text = ctk.CTkTextbox(form_frame, width=600, height=80)
        self.env_text.pack(anchor="w", pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        create_btn = ctk.CTkButton(
            button_frame,
            text="[+] Create Server",
            width=150,
            command=self._create_server
        )
        create_btn.pack(side="left", padx=20, pady=15)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            command=self._close_dialog
        )
        close_btn.pack(side="right", padx=20, pady=15)
    
    def _create_server(self):
        """Create the custom server configuration"""
        try:
            # Validate inputs
            name = self.name_entry.get().strip()
            if not name:
                self._show_error("Server name is required")
                return
            
            server_type = self.type_combo.get()
            description = self.description_text.get("0.0", "end").strip()
            package = self.package_entry.get().strip()
            command = self.command_entry.get().strip()
            
            # Parse arguments
            args_text = self.args_text.get("0.0", "end").strip()
            args = [arg.strip() for arg in args_text.split('\n') if arg.strip()] if args_text else []
            
            # Parse environment variables
            env_text = self.env_text.get("0.0", "end").strip()
            env = {}
            if env_text:
                for line in env_text.split('\n'):
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env[key.strip()] = value.strip()
            
            # Create server configuration
            server_config = {
                "name": name,
                "description": description or "Custom MCP server",
                "type": server_type,
                "category": "custom",
                "configuration": {
                    "command": command,
                    "args": args,
                    "env": env
                }
            }
            
            # Add type-specific fields
            if server_type in ["npm", "python"] and package:
                server_config["package"] = package
            elif server_type == "git" and package:
                server_config["repository"] = package
            elif server_type == "docker" and package:
                server_config["image"] = package
            
            # Save to local catalog
            self._save_to_catalog(server_config)
            
            self._show_success(f"Custom server '{name}' created successfully!")
            
        except Exception as e:
            self.logger.error("Failed to create custom server", e)
            self._show_error(f"Failed to create server: {str(e)}")
    
    def _save_to_catalog(self, server_config: Dict):
        """Save custom server to local catalog"""
        try:
            catalog_file = Path("config/servers.json")
            
            # Load existing catalog
            if catalog_file.exists():
                with open(catalog_file, 'r', encoding='utf-8') as f:
                    catalog = json.load(f)
            else:
                catalog = {"servers": {}, "categories": {}}
            
            # Add server to catalog
            server_id = server_config["name"].lower().replace(" ", "_")
            catalog["servers"][server_id] = server_config
            
            # Add custom category if not exists
            if "custom" not in catalog.get("categories", {}):
                catalog.setdefault("categories", {})["custom"] = {
                    "name": "Custom Servers",
                    "description": "User-created server configurations"
                }
            
            # Save catalog
            catalog_file.parent.mkdir(exist_ok=True)
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            
            self.logger.log_user_action(f"Custom server created: {server_config['name']}")
            
        except Exception as e:
            self.logger.error("Failed to save server to catalog", e)
            raise
    
    def _show_error(self, message: str):
        """Show error message"""
        error_dialog = ctk.CTkToplevel(self.dialog)
        error_dialog.title("Error")
        error_dialog.geometry("400x150")
        error_dialog.transient(self.dialog)
        error_dialog.grab_set()
        
        ctk.CTkLabel(error_dialog, text="[X] Error", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        ctk.CTkLabel(error_dialog, text=message, wraplength=350).pack(pady=10)
        ctk.CTkButton(error_dialog, text="OK", command=error_dialog.destroy).pack(pady=20)
    
    def _show_success(self, message: str):
        """Show success message"""
        success_dialog = ctk.CTkToplevel(self.dialog)
        success_dialog.title("Success")
        success_dialog.geometry("400x150")
        success_dialog.transient(self.dialog)
        success_dialog.grab_set()
        
        ctk.CTkLabel(success_dialog, text="[+] Success", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        ctk.CTkLabel(success_dialog, text=message, wraplength=350).pack(pady=10)
        
        def close_both():
            success_dialog.destroy()
            self.dialog.destroy()
        
        ctk.CTkButton(success_dialog, text="OK", command=close_both).pack(pady=20)
    
    def _close_dialog(self):
        """Close the dialog"""
        self.dialog.destroy()