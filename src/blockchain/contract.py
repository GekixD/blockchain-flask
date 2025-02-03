import hashlib
import time
import ast
import signal
from contextlib import contextmanager
from typing import Dict, Any, Optional, NoReturn, Generator
from src.utils.logger import setup_logger

logger = setup_logger('blockchain.contract')

@contextmanager
def timeout(seconds: int) -> Generator[None, None, None]:
    def timeout_handler(signum: int, frame: Any) -> NoReturn:
        logger.debug(f"Timeout triggered by signal {signum}")
        logger.debug(f"At execution frame: {frame.f_code.co_name}")
        raise TimeoutError("Execution timed out")
    
    logger.debug("Setting up timeout handler")
    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        logger.debug("Yielding to wrapped code")
        yield
        logger.debug("Wrapped code completed successfully")
    finally:
        logger.debug("Cleaning up timeout handler")
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)

class SmartContract:
    def __init__(self, code: str, owner: str):
        self.code = code
        self.owner = owner
        self.address = self._generate_address()
        self.state = {}
        self.created_at = time.time()
        self.gas_used = 0
        self.last_execution = None
        
    def _generate_address(self) -> str:
        unique_string = f"{self.owner}{self.code}{time.time()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()
        
    def _validate_syntax(self) -> bool:
        try:
            ast.parse(self.code)
            return True
        except SyntaxError as e:
            logger.error(f"Contract syntax error: {str(e)}")
            return False
            
    def _validate_security(self) -> Optional[str]:
        prohibited = ['import', 'eval', 'exec', '__', 'open', 
                     'file', 'system', 'subprocess']
        
        for item in prohibited:
            if item in self.code:
                logger.error(f"Prohibited operation found: {item}")
                return f"Prohibited operation: {item}"
        return None
        
    def validate(self) -> tuple[bool, Optional[str]]:
        logger.info(f"Validating contract {self.address}")
        
        if not self._validate_syntax():
            return False, "Invalid syntax"
            
        security_error = self._validate_security()
        if security_error:
            return False, security_error
            
        return True, None
        
    def execute(self, blockchain, params: dict) -> tuple[dict, float]:
        logger.info(f"Executing contract {self.address}")
        start_time = time.time()
        
        try:
            # Create restricted environment
            safe_globals = self._create_safe_environment(blockchain, params)
            
            # Execute with timeout
            try:
                with timeout(seconds=2):  # TODO: make timeout configurable or dynamic
                    exec(self.code, safe_globals, {})
            except TimeoutError as e:
                logger.error(f"Contract execution timed out: {str(e)}")
                raise Exception("Contract execution timed out")
                
            execution_time = time.time() - start_time
            self.gas_used += execution_time * 1000  # Convert to milliseconds
            self.last_execution = time.time()
            
            logger.info(f"Contract executed successfully. Gas used: {self.gas_used}")
            return self.state, self.gas_used
            
        except Exception as e:
            logger.error(f"Contract execution failed: {str(e)}")
            raise Exception(str(e))
            
    def _create_safe_environment(self, blockchain, params: dict) -> dict:
        return {
            'blockchain': BlockchainInterface(blockchain),
            'params': params.copy(),
            'state': self.state,
            'now': time.time,
            'sender': params.get('sender'),
        }
        
class BlockchainInterface:
    def __init__(self, blockchain):
        self._blockchain = blockchain
        
    def get_balance(self, address: str) -> float:
        return self._blockchain.get_user_balance(address)
        
    def get_block_number(self) -> int:
        return len(self._blockchain.chain)
