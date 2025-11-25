"""
Logging Configuration - Observability setup for EduAssist AI

This provides:
1. Structured logging for all agents
2. Tracing of agent interactions
3. Performance metrics
4. Debug information for development

This demonstrates: Observability (Logging, Tracing, Metrics)
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional
from pathlib import Path


def setup_logging(
    level: str = None,
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> logging.Logger:
    """
    Set up comprehensive logging for the EduAssist AI system
    
    This creates a hierarchical logging system where:
    - Each agent has its own logger
    - All logs are captured at the root level
    - Logs can go to both console and file
    - Different log levels for development vs production
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, uses EDUASSIST_LOG_LEVEL env var or defaults to WARNING for clean output
        log_file: Optional path to log file
        enable_console: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    
    # Determine log level - prioritize clean user experience
    if level is None:
        # Check environment variable
        level = os.getenv('EDUASSIST_LOG_LEVEL', 'WARNING')
    
    # Create logs directory if using file logging
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatter with detailed information
    # This format includes: timestamp, logger name, level, and message
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Simpler formatter for console (more readable)
    simple_formatter = logging.Formatter(
        fmt='%(levelname)-8s | %(name)-15s | %(message)s'
    )
    
    # Console Handler (for real-time monitoring)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File Handler (for persistent logs)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)  # Capture all details in file
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Create application logger
    app_logger = logging.getLogger('eduassist')
    
    # Only show init message if level is INFO or DEBUG
    if level.upper() in ['INFO', 'DEBUG']:
        app_logger.info("="*60)
        app_logger.info("EduAssist AI Logging System Initialized")
        app_logger.info(f"Log Level: {level}")
        app_logger.info(f"Console Output: {enable_console}")
        app_logger.info(f"File Output: {log_file if log_file else 'Disabled'}")
        app_logger.info("="*60)
    
    return app_logger


class AgentTracer:
    """
    Utility class for tracing agent interactions
    
    This helps with observability by tracking:
    - Which agents are invoked
    - What actions they perform
    - How long operations take
    - What data flows between agents
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize tracer for a specific agent
        
        Args:
            agent_name: Name of the agent being traced
        """
        self.agent_name = agent_name
        self.logger = logging.getLogger(f'eduassist.{agent_name}')
        self.traces = []
    
    def log_action(self, 
                   action: str, 
                   details: Optional[dict] = None,
                   level: str = "INFO"):
        """
        Log an agent action
        
        Args:
            action: Description of the action
            details: Optional dict with additional details
            level: Log level
        """
        timestamp = datetime.now().isoformat()
        
        log_message = f"[{self.agent_name}] {action}"
        if details:
            log_message += f" | {details}"
        
        # Log at appropriate level
        log_method = getattr(self.logger, level.lower())
        log_method(log_message)
        
        # Store in trace history
        self.traces.append({
            'timestamp': timestamp,
            'agent': self.agent_name,
            'action': action,
            'details': details,
            'level': level
        })
    
    def log_start(self, operation: str):
        """Log the start of an operation"""
        self.log_action(f"START: {operation}", level="INFO")
    
    def log_end(self, operation: str, success: bool = True):
        """Log the end of an operation"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action(f"END: {operation} - {status}", level="INFO" if success else "WARNING")
    
    def log_error(self, error: str, exception: Optional[Exception] = None):
        """Log an error"""
        details = {'error': error}
        if exception:
            details['exception'] = str(exception)
        
        self.log_action("ERROR", details=details, level="ERROR")
        
        if exception:
            self.logger.exception(f"[{self.agent_name}] Exception details:")
    
    def get_trace_history(self) -> list:
        """Get all traces for this agent"""
        return self.traces.copy()
    
    def clear_traces(self):
        """Clear trace history"""
        self.traces.clear()


class PerformanceMetrics:
    """
    Track performance metrics for the agent system
    
    Metrics include:
    - Response times
    - Agent invocation counts
    - Success/failure rates
    - Token usage (if tracked)
    """
    
    def __init__(self):
        """Initialize metrics tracking"""
        self.logger = logging.getLogger('eduassist.metrics')
        
        self.metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'total_response_time': 0,
            'agent_invocations': {},
            'average_response_time': 0
        }
    
    def record_query(self, 
                    success: bool,
                    response_time: float,
                    agents_used: list):
        """
        Record metrics for a query
        
        Args:
            success: Whether query was successful
            response_time: Time taken in seconds
            agents_used: List of agents that were invoked
        """
        self.metrics['total_queries'] += 1
        
        if success:
            self.metrics['successful_queries'] += 1
        else:
            self.metrics['failed_queries'] += 1
        
        self.metrics['total_response_time'] += response_time
        self.metrics['average_response_time'] = (
            self.metrics['total_response_time'] / self.metrics['total_queries']
        )
        
        # Track agent invocations
        for agent in agents_used:
            if agent not in self.metrics['agent_invocations']:
                self.metrics['agent_invocations'][agent] = 0
            self.metrics['agent_invocations'][agent] += 1
        
        # Log metrics periodically (every 10 queries)
        if self.metrics['total_queries'] % 10 == 0:
            self.log_metrics_summary()
    
    def log_metrics_summary(self):
        """Log a summary of current metrics"""
        self.logger.info("="*60)
        self.logger.info("PERFORMANCE METRICS SUMMARY")
        self.logger.info(f"Total Queries: {self.metrics['total_queries']}")
        self.logger.info(f"Success Rate: {self._calculate_success_rate():.1f}%")
        self.logger.info(f"Average Response Time: {self.metrics['average_response_time']:.2f}s")
        self.logger.info(f"Agent Invocations: {self.metrics['agent_invocations']}")
        self.logger.info("="*60)
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.metrics['total_queries'] == 0:
            return 0.0
        
        return (self.metrics['successful_queries'] / self.metrics['total_queries']) * 100
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'total_response_time': 0,
            'agent_invocations': {},
            'average_response_time': 0
        }
        self.logger.info("Metrics reset")


# Global metrics instance
_metrics_instance = None

def get_metrics() -> PerformanceMetrics:
    """Get the global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PerformanceMetrics()
    return _metrics_instance


# Example usage in agents:
# from utils.logging_config import AgentTracer
#
# tracer = AgentTracer('research')
# tracer.log_start('web_search')
# # ... do work ...
# tracer.log_end('web_search', success=True)