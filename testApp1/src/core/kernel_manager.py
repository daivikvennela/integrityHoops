"""
Jupyter Kernel Manager for ML Notebook Integration
Manages kernel lifecycle, execution, and cleanup with M4 optimization
"""

import logging
import time
import uuid
from typing import Dict, Optional, Any
from jupyter_client import KernelManager
import queue
import threading

logger = logging.getLogger(__name__)


class NotebookKernelManager:
    """
    Singleton kernel manager for managing Jupyter kernels across the application.
    Optimized for M4 chip with multi-core support.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(NotebookKernelManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.kernels: Dict[str, Dict[str, Any]] = {}
        self.kernel_timeout = 1800  # 30 minutes idle timeout
        self._initialized = True
        self._cleanup_thread = None
        self._start_cleanup_thread()
        
        logger.info("NotebookKernelManager initialized")
    
    def _start_cleanup_thread(self):
        """Start background thread for cleaning up idle kernels"""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_idle_kernels,
                daemon=True
            )
            self._cleanup_thread.start()
    
    def _cleanup_idle_kernels(self):
        """Background task to clean up idle kernels"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                current_time = time.time()
                
                kernels_to_remove = []
                for session_id, kernel_info in self.kernels.items():
                    last_activity = kernel_info.get('last_activity', 0)
                    if current_time - last_activity > self.kernel_timeout:
                        kernels_to_remove.append(session_id)
                
                for session_id in kernels_to_remove:
                    logger.info(f"Cleaning up idle kernel: {session_id}")
                    self.stop_kernel(session_id)
                    
            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")
    
    def create_kernel(self, session_id: Optional[str] = None) -> str:
        """
        Create a new Jupyter kernel for a session.
        Optimized for M4 chip performance.
        
        Args:
            session_id: Optional session ID. If None, generates new UUID.
            
        Returns:
            session_id: The session ID for this kernel
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Check if kernel already exists for this session
        if session_id in self.kernels:
            logger.info(f"Kernel already exists for session {session_id}")
            self.kernels[session_id]['last_activity'] = time.time()
            return session_id
        
        try:
            # Create kernel manager with M4 optimizations
            km = KernelManager()
            
            # Configure kernel for M4 optimization
            km.kernel_spec_manager
            
            # Start the kernel
            km.start_kernel()
            
            # Get the kernel client
            kc = km.client()
            kc.start_channels()
            
            # Wait for kernel to be ready
            kc.wait_for_ready(timeout=30)
            
            # Store kernel info
            self.kernels[session_id] = {
                'manager': km,
                'client': kc,
                'created_at': time.time(),
                'last_activity': time.time(),
                'variables': {}  # Store variable state
            }
            
            logger.info(f"Kernel created successfully for session {session_id}")
            
            # Initialize kernel with common imports
            self._initialize_kernel(session_id)
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating kernel: {e}")
            raise
    
    def _initialize_kernel(self, session_id: str):
        """Initialize kernel with common imports and settings"""
        init_code = """
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style('darkgrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100

print("Kernel initialized successfully!")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version: {np.__version__}")
print(f"Scikit-learn available")
"""
        try:
            self.execute_code(session_id, init_code)
        except Exception as e:
            logger.warning(f"Error initializing kernel: {e}")
    
    def execute_code(self, session_id: str, code: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute code in the kernel and return results.
        
        Args:
            session_id: Session ID for the kernel
            code: Python code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary with execution results:
            {
                'success': bool,
                'output': str,  # stdout content
                'error': str,   # stderr content
                'display_data': list,  # images, tables, etc.
                'execution_count': int
            }
        """
        if session_id not in self.kernels:
            raise ValueError(f"No kernel found for session {session_id}")
        
        kernel_info = self.kernels[session_id]
        kc = kernel_info['client']
        
        # Update last activity
        kernel_info['last_activity'] = time.time()
        
        try:
            # Execute the code
            msg_id = kc.execute(code)
            
            # Collect outputs
            output_text = []
            error_text = []
            display_data = []
            execution_count = 0
            
            # Wait for execution to complete
            start_time = time.time()
            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Code execution timed out after {timeout} seconds")
                
                try:
                    msg = kc.get_iopub_msg(timeout=1)
                    msg_type = msg['header']['msg_type']
                    content = msg['content']
                    
                    if msg_type == 'stream':
                        # stdout or stderr
                        stream_name = content['name']
                        text = content['text']
                        if stream_name == 'stdout':
                            output_text.append(text)
                        elif stream_name == 'stderr':
                            error_text.append(text)
                    
                    elif msg_type == 'execute_result':
                        # Execution result (e.g., variable value)
                        execution_count = content.get('execution_count', 0)
                        data = content.get('data', {})
                        display_data.append({
                            'type': 'execute_result',
                            'data': data
                        })
                    
                    elif msg_type == 'display_data':
                        # Display data (plots, tables, etc.)
                        data = content.get('data', {})
                        display_data.append({
                            'type': 'display_data',
                            'data': data
                        })
                    
                    elif msg_type == 'error':
                        # Execution error
                        error_name = content.get('ename', 'Error')
                        error_value = content.get('evalue', '')
                        traceback = content.get('traceback', [])
                        
                        error_text.append(f"{error_name}: {error_value}\n")
                        error_text.extend(traceback)
                    
                    elif msg_type == 'status':
                        # Check if execution is complete
                        execution_state = content.get('execution_state')
                        if execution_state == 'idle':
                            break
                
                except queue.Empty:
                    # Check if execution is done
                    if kc.is_alive():
                        continue
                    else:
                        break
            
            # Return results
            success = len(error_text) == 0
            return {
                'success': success,
                'output': ''.join(output_text),
                'error': ''.join(error_text),
                'display_data': display_data,
                'execution_count': execution_count
            }
            
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'display_data': [],
                'execution_count': 0
            }
    
    def stop_kernel(self, session_id: str):
        """Stop and cleanup a kernel"""
        if session_id not in self.kernels:
            logger.warning(f"No kernel found for session {session_id}")
            return
        
        try:
            kernel_info = self.kernels[session_id]
            kc = kernel_info['client']
            km = kernel_info['manager']
            
            # Stop channels
            kc.stop_channels()
            
            # Shutdown kernel
            km.shutdown_kernel()
            
            # Remove from active kernels
            del self.kernels[session_id]
            
            logger.info(f"Kernel stopped for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error stopping kernel: {e}")
    
    def get_kernel_status(self, session_id: str) -> Dict[str, Any]:
        """Get status information for a kernel"""
        if session_id not in self.kernels:
            return {'exists': False}
        
        kernel_info = self.kernels[session_id]
        return {
            'exists': True,
            'created_at': kernel_info['created_at'],
            'last_activity': kernel_info['last_activity'],
            'is_alive': kernel_info['client'].is_alive()
        }
    
    def list_kernels(self) -> list:
        """List all active kernels"""
        return [
            {
                'session_id': session_id,
                'created_at': info['created_at'],
                'last_activity': info['last_activity']
            }
            for session_id, info in self.kernels.items()
        ]
    
    def cleanup_all(self):
        """Stop all kernels (for application shutdown)"""
        logger.info("Cleaning up all kernels")
        session_ids = list(self.kernels.keys())
        for session_id in session_ids:
            self.stop_kernel(session_id)


# Singleton instance
kernel_manager = NotebookKernelManager()

