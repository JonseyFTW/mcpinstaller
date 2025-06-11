"""
Comprehensive logging system for MCP Installer
Provides detailed logging with automatic log rotation and multiple log levels
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class MCPLogger:
    """Enhanced logging system for MCP Installer with multiple log files and console output"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize different loggers for different purposes
        self.main_logger = self._setup_logger("main", "mcp_installer.log")
        self.system_logger = self._setup_logger("system", "system_check.log")
        self.install_logger = self._setup_logger("install", "installations.log")
        self.error_logger = self._setup_logger("error", "errors.log", level=logging.ERROR)
        
        # Console handler for immediate feedback
        self.console_handler = self._setup_console_handler()
        
        # Add console handler to main logger
        self.main_logger.addHandler(self.console_handler)
        
    def _setup_logger(self, name: str, filename: str, level: int = logging.INFO) -> logging.Logger:
        """Set up a logger with file rotation"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
            
        # File handler with rotation
        file_path = self.log_dir / filename
        file_handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=10*1024*1024, backupCount=5  # 10MB max, 5 backups
        )
        
        # Detailed format for file logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-10s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _setup_console_handler(self) -> logging.StreamHandler:
        """Set up console handler with Windows encoding support"""
        # Handle Windows console encoding issues
        if sys.platform == "win32":
            import codecs
            import io
            
            # Create a UTF-8 wrapper for stdout to handle Unicode characters
            if hasattr(sys.stdout, 'buffer'):
                stdout_wrapper = io.TextIOWrapper(
                    sys.stdout.buffer, 
                    encoding='utf-8', 
                    errors='replace'
                )
            else:
                stdout_wrapper = sys.stdout
                
            console_handler = logging.StreamHandler(stdout_wrapper)
        else:
            console_handler = logging.StreamHandler(sys.stdout)
            
        console_handler.setLevel(logging.INFO)
        
        # Simple format for console
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        return console_handler
    
    def info(self, message: str, category: str = "main"):
        """Log info message"""
        logger = getattr(self, f"{category}_logger", self.main_logger)
        logger.info(message)
    
    def warning(self, message: str, category: str = "main"):
        """Log warning message"""
        logger = getattr(self, f"{category}_logger", self.main_logger)
        logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None, category: str = "main"):
        """Log error message with optional exception details"""
        logger = getattr(self, f"{category}_logger", self.main_logger)
        
        if exception:
            logger.error(f"{message} | Exception: {str(exception)}")
            # Also log to error logger
            self.error_logger.error(f"{message} | Exception: {str(exception)}")
        else:
            logger.error(message)
            self.error_logger.error(message)
    
    def debug(self, message: str, category: str = "main"):
        """Log debug message"""
        logger = getattr(self, f"{category}_logger", self.main_logger)
        logger.debug(message)
    
    def log_user_action(self, action: str, details: str = ""):
        """Log user interactions for debugging"""
        message = f"USER ACTION: {action}"
        if details:
            message += f" | Details: {details}"
        self.info(message)
    
    def log_command_execution(self, command: str, exit_code: int, output: str = "", error: str = ""):
        """Log command execution details"""
        message = f"COMMAND: {command} | Exit Code: {exit_code}"
        
        if output:
            message += f" | Output: {output[:500]}"  # Limit output length
        
        if error:
            message += f" | Error: {error[:500]}"
            self.error(message, category="install")
        else:
            self.info(message, category="install")
    
    def log_system_info(self, component: str, status: str, details: str = ""):
        """Log system checking information"""
        message = f"SYSTEM CHECK: {component} | Status: {status}"
        if details:
            message += f" | Details: {details}"
        self.info(message, category="system")
    
    def log_server_operation(self, operation: str, server_name: str, result: str):
        """Log MCP server operations"""
        message = f"SERVER {operation.upper()}: {server_name} | Result: {result}"
        self.info(message, category="install")
    
    def start_session(self):
        """Log session start"""
        self.info("="*60)
        self.info("MCP INSTALLER SESSION STARTED")
        self.info(f"Timestamp: {datetime.now().isoformat()}")
        self.info(f"Python Version: {sys.version}")
        self.info(f"Platform: {sys.platform}")
        self.info("="*60)
    
    def end_session(self):
        """Log session end"""
        self.info("="*60)
        self.info("MCP INSTALLER SESSION ENDED")
        self.info(f"Timestamp: {datetime.now().isoformat()}")
        self.info("="*60)


# Global logger instance
logger_instance: Optional[MCPLogger] = None

def get_logger() -> MCPLogger:
    """Get the global logger instance"""
    global logger_instance
    if logger_instance is None:
        logger_instance = MCPLogger()
    return logger_instance

def init_logging(log_dir: str = "logs") -> MCPLogger:
    """Initialize the logging system"""
    global logger_instance
    logger_instance = MCPLogger(log_dir)
    logger_instance.start_session()
    return logger_instance