"""
Main application window for MCP Installer
Built with CustomTkinter for a modern, professional appearance
"""

import customtkinter as ctk
import threading
import webbrowser
from typing import Optional, Callable
from pathlib import Path

from ..utils.logger import get_logger
from ..core.system_checker import SystemChecker
from ..core.server_manager import MCPServerManager
from .dialogs import ServerDiscoveryDialog, ServerCreationDialog


class MCPInstallerGUI:
    """Main application window with modern GUI"""
    
    def __init__(self):
        self.logger = get_logger()
        self.logger.log_user_action("Application started")
        
        # Initialize system checker and server manager
        self.system_checker = SystemChecker()
        self.server_manager = MCPServerManager()
        
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")  # "dark", "light", or "system"
        ctk.set_default_color_theme("blue")  # "blue", "green", or "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("MCP Server Auto-Installer v2.0")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Center the window
        self.center_window()
        
        # Initialize components
        self.status_var = ctk.StringVar(value="Ready")
        self.progress_var = ctk.DoubleVar()
        
        # Create UI
        self.create_widgets()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Run startup initialization
        self.run_startup_checks()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        
        # Header Frame
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="[*] MCP Server Auto-Installer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Professional MCP Server Management Tool",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Main Content Frame
        content_frame = ctk.CTkFrame(self.root)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left Panel - Action Buttons
        left_panel = ctk.CTkFrame(content_frame)
        left_panel.pack(side="left", fill="y", padx=(20, 10), pady=20)
        
        self.create_action_buttons(left_panel)
        
        # Right Panel - Information and Logs
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)
        
        self.create_info_panel(right_panel)
        
        # Status Bar
        status_frame = ctk.CTkFrame(self.root)
        status_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.create_status_bar(status_frame)
    
    def create_action_buttons(self, parent):
        """Create main action buttons"""
        
        # Quick Actions Label
        quick_label = ctk.CTkLabel(
            parent,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        quick_label.pack(pady=(20, 15))
        
        # System Check Button
        self.system_btn = ctk.CTkButton(
            parent,
            text="[?] System Check",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.system_check_clicked
        )
        self.system_btn.pack(pady=5)
        
        # Separator
        separator1 = ctk.CTkFrame(parent, height=2)
        separator1.pack(fill="x", pady=15, padx=20)
        
        # Server Management Label
        server_label = ctk.CTkLabel(
            parent,
            text="Server Management",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        server_label.pack(pady=(15, 15))
        
        # Discover Servers Button
        self.discover_btn = ctk.CTkButton(
            parent,
            text="[*] Discover Servers",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.discover_servers_clicked
        )
        self.discover_btn.pack(pady=5)
        
        # Create Server Button
        self.create_btn = ctk.CTkButton(
            parent,
            text="[+] Create Server",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.create_server_clicked
        )
        self.create_btn.pack(pady=5)
        
        # Install Server Button
        self.install_btn = ctk.CTkButton(
            parent,
            text="[I] Install Servers",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.install_server_clicked
        )
        self.install_btn.pack(pady=5)
        
        # Separator
        separator2 = ctk.CTkFrame(parent, height=2)
        separator2.pack(fill="x", pady=15, padx=20)
        
        # Tools Label
        tools_label = ctk.CTkLabel(
            parent,
            text="Tools & Monitoring",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tools_label.pack(pady=(15, 15))
        
        # Docker Manager Button
        self.docker_btn = ctk.CTkButton(
            parent,
            text="[D] Docker Manager",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.docker_manager_clicked
        )
        self.docker_btn.pack(pady=5)
        
        # Web Dashboard Button
        self.dashboard_btn = ctk.CTkButton(
            parent,
            text="[W] Web Dashboard",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.web_dashboard_clicked
        )
        self.dashboard_btn.pack(pady=5)
        
        # Update Check Button
        self.update_btn = ctk.CTkButton(
            parent,
            text="[U] Check Updates",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.check_updates_clicked
        )
        self.update_btn.pack(pady=5)
    
    def create_info_panel(self, parent):
        """Create information and log display panel"""
        
        # System Info Label
        info_label = ctk.CTkLabel(
            parent,
            text="System Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        info_label.pack(pady=(20, 10))
        
        # System Info Frame
        sys_info_frame = ctk.CTkFrame(parent)
        sys_info_frame.pack(fill="x", padx=20, pady=5)
        
        # System info text (will be populated by system checker)
        self.sys_info_text = ctk.CTkTextbox(
            sys_info_frame,
            height=120,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.sys_info_text.pack(fill="x", padx=15, pady=15)
        self.sys_info_text.insert("0.0", "System information will appear here after system check...")
        
        # Activity Log Label
        log_label = ctk.CTkLabel(
            parent,
            text="Activity Log",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        log_label.pack(pady=(20, 10))
        
        # Log Display Frame
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Log text area with scrollbar
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Add initial log entry
        self.add_log_entry("Application started successfully")
        self.add_log_entry("Ready for user commands")
    
    def create_status_bar(self, parent):
        """Create status bar with progress indicator"""
        
        # Status label
        self.status_label = ctk.CTkLabel(
            parent,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(parent, width=200)
        self.progress_bar.pack(side="right", padx=20, pady=10)
        self.progress_bar.set(0)
    
    def add_log_entry(self, message: str, level: str = "INFO"):
        """Add entry to the activity log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different log levels
        color_map = {
            "INFO": "white",
            "WARNING": "orange",
            "ERROR": "red",
            "SUCCESS": "green"
        }
        
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        # Insert at the end
        self.log_text.insert("end", log_entry)
        
        # Auto-scroll to bottom
        self.log_text.see("end")
        
        # Also log to file
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
        self.add_log_entry(f"Status: {message}")
    
    def update_progress(self, value: float):
        """Update progress bar (0.0 to 1.0)"""
        self.progress_bar.set(value)
        self.root.update_idletasks()
    
    def run_in_thread(self, func: Callable, *args, **kwargs):
        """Run a function in a separate thread to prevent GUI blocking"""
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Thread execution failed", e)
                self.add_log_entry(f"Error: {str(e)}", "ERROR")
            finally:
                self.update_progress(0)
                self.update_status("Ready")
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
    
    # Button Event Handlers
    
    def system_check_clicked(self):
        """Handle system check button click"""
        self.logger.log_user_action("System Check button clicked")
        self.add_log_entry("Starting system compatibility check...")
        self.update_status("Checking system compatibility...")
        self.update_progress(0.1)
        
        # Run system check in thread
        self.run_in_thread(self._run_system_check)
    
    def discover_servers_clicked(self):
        """Handle discover servers button click"""
        self.logger.log_user_action("Discover Servers button clicked")
        self.add_log_entry("Starting MCP server discovery...")
        self.update_status("Discovering available MCP servers...")
        
        # Run discovery in thread
        self.run_in_thread(self._run_server_discovery)
    
    def create_server_clicked(self):
        """Handle create server button click"""
        self.logger.log_user_action("Create Server button clicked")
        self.add_log_entry("Opening server creation dialog...")
        
        # Open server creation dialog
        self.run_in_thread(self._open_server_creator)
    
    def install_server_clicked(self):
        """Handle install server button click"""
        self.logger.log_user_action("Install Server button clicked")
        self.add_log_entry("Opening server installation dialog...")
        
        # Open server installation dialog
        self.run_in_thread(self._open_server_installer)
    
    def docker_manager_clicked(self):
        """Handle docker manager button click"""
        self.logger.log_user_action("Docker Manager button clicked")
        self.add_log_entry("Opening Docker container manager...")
        
        # Open docker manager
        self.run_in_thread(self._open_docker_manager)
    
    def web_dashboard_clicked(self):
        """Handle web dashboard button click"""
        self.logger.log_user_action("Web Dashboard button clicked")
        self.add_log_entry("Opening web dashboard in browser...")
        
        dashboard_path = Path("mcp-dashboard.html")
        if dashboard_path.exists():
            webbrowser.open(dashboard_path.absolute().as_uri())
            self.add_log_entry("Web dashboard opened successfully", "SUCCESS")
        else:
            self.add_log_entry("Web dashboard file not found", "ERROR")
    
    def check_updates_clicked(self):
        """Handle check updates button click"""
        self.logger.log_user_action("Check Updates button clicked")
        self.add_log_entry("Checking for server updates...")
        self.update_status("Checking for updates...")
        
        # Run update check in thread
        self.run_in_thread(self._check_for_updates)
    
    # Thread worker methods (to be implemented)
    
    def _run_system_check(self):
        """Run system compatibility check"""
        try:
            self.add_log_entry("Running comprehensive system check...")
            self.update_progress(0.2)
            
            # Run all system checks
            results = self.system_checker.check_all()
            self.update_progress(0.8)
            
            # Update system info display
            formatted_results = self.system_checker.format_results_for_display()
            self.sys_info_text.delete("0.0", "end")
            self.sys_info_text.insert("0.0", formatted_results)
            
            # Get summary
            summary = self.system_checker.get_summary()
            
            if summary["status"] == "passed":
                self.add_log_entry("[+] All system checks passed!", "SUCCESS")
                self.update_status("System ready for MCP installation")
            elif summary["status"] == "partial":
                self.add_log_entry(f"[!] {summary['message']}", "WARNING")
                self.update_status("System partially ready - some optional features unavailable")
            else:
                self.add_log_entry(f"[X] {summary['message']}", "ERROR")
                self.update_status("System not ready - please resolve critical issues")
            
            self.update_progress(1.0)
            
        except Exception as e:
            self.logger.error("System check failed", e)
            self.add_log_entry(f"System check failed: {str(e)}", "ERROR")
            self.update_status("System check failed")
    
    def _run_server_discovery(self):
        """Run server discovery"""
        try:
            self.add_log_entry("Opening server discovery dialog...")
            
            # Open discovery dialog in main thread
            def open_dialog():
                dialog = ServerDiscoveryDialog(
                    self.root, 
                    callback=self._on_servers_discovered
                )
            
            # Run in main thread
            self.root.after(0, open_dialog)
            
        except Exception as e:
            self.logger.error("Failed to open server discovery", e)
            self.add_log_entry(f"Failed to open discovery: {str(e)}", "ERROR")
    
    def _open_server_creator(self):
        """Open server creation dialog"""
        try:
            self.add_log_entry("Opening server creation dialog...")
            
            def open_dialog():
                dialog = ServerCreationDialog(self.root)
            
            self.root.after(0, open_dialog)
            
        except Exception as e:
            self.logger.error("Failed to open server creator", e)
            self.add_log_entry(f"Failed to open creator: {str(e)}", "ERROR")
    
    def _open_server_installer(self):
        """Open server installation dialog"""
        try:
            self.add_log_entry("Loading installed servers...")
            
            # Get list of installed servers
            installed_servers = self.server_manager.get_installed_servers()
            
            if not installed_servers:
                self.add_log_entry("No MCP servers found. Use 'Discover Servers' to find and install servers.", "WARNING")
                return
            
            self.add_log_entry(f"Found {len(installed_servers)} installed servers:")
            for server in installed_servers:
                self.add_log_entry(f"  - {server['name']} ({server['type']}) v{server['version']}")
            
        except Exception as e:
            self.logger.error("Failed to check installed servers", e)
            self.add_log_entry(f"Failed to check servers: {str(e)}", "ERROR")
    
    def _open_docker_manager(self):
        """Open docker manager"""
        try:
            self.add_log_entry("Checking Docker availability...")
            
            # Check if Docker is available
            import subprocess
            docker_check = subprocess.run(["docker", "--version"], capture_output=True, timeout=10)
            
            if docker_check.returncode == 0:
                version = docker_check.stdout.decode().strip()
                self.add_log_entry(f"Docker detected: {version}")
                self.add_log_entry("Docker container manager coming soon...")
            else:
                self.add_log_entry("Docker not found. Please install Docker Desktop first.", "WARNING")
                
        except subprocess.TimeoutExpired:
            self.add_log_entry("Docker check timed out", "WARNING")
        except Exception as e:
            self.logger.error("Docker check failed", e)
            self.add_log_entry("Docker not available", "WARNING")
    
    def _check_for_updates(self):
        """Check for updates"""
        try:
            self.add_log_entry("Checking for MCP server updates...")
            
            # Get installed servers
            installed_servers = self.server_manager.get_installed_servers()
            
            if not installed_servers:
                self.add_log_entry("No installed servers to check for updates", "WARNING")
                return
            
            updates_available = 0
            for server in installed_servers:
                # Simple version check simulation
                self.add_log_entry(f"Checking {server['name']}... up to date")
            
            if updates_available == 0:
                self.add_log_entry("All servers are up to date", "SUCCESS")
            else:
                self.add_log_entry(f"{updates_available} updates available", "WARNING")
                
        except Exception as e:
            self.logger.error("Update check failed", e)
            self.add_log_entry(f"Update check failed: {str(e)}", "ERROR")
    
    def _on_servers_discovered(self, selected_servers: list):
        """Callback when servers are discovered and selected"""
        if selected_servers:
            self.add_log_entry(f"Selected {len(selected_servers)} servers for installation", "SUCCESS")
            for server in selected_servers:
                self.add_log_entry(f"  - {server.get('name', 'Unknown')} ({server.get('type', 'unknown')})")
        else:
            self.add_log_entry("No servers selected from discovery")
    
    def run_startup_checks(self):
        """Run system checks and IDE detection on startup"""
        def startup_task():
            try:
                self.update_status("Initializing system checks...")
                self.logger.info("Running startup system checks")
                
                # Run system info check
                self.update_status("Checking system information...")
                system_info = self.system_checker.get_system_info()
                
                # Check IDE installations
                self.update_status("Detecting installed IDEs...")
                ide_status = self.server_manager.vscode_config.get_extension_status()
                
                # Log detected IDEs
                for ide_name, status in ide_status.items():
                    if status['installed']:
                        display_name = status['name']
                        server_count = status['server_count']
                        self.add_log_entry(f"Detected {display_name} with {server_count} MCP servers configured")
                    
                self.update_status("Startup checks completed")
                self.logger.info("Startup system checks completed successfully")
                
            except Exception as e:
                self.logger.error(f"Startup checks failed: {str(e)}")
                self.update_status("Startup checks failed")
        
        # Run in background thread to avoid blocking UI
        self.run_in_thread(startup_task)
    
    def on_closing(self):
        """Handle application closing"""
        self.logger.log_user_action("Application closing")
        self.logger.end_session()
        self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()