from flask import request, Blueprint, Response
from typing import Tuple, Dict, List, Any, Optional
from src.blockchain.blockchain import Blockchain
from src.blockchain.helpers import make_response, validate_fields, hash_block
from src.config.config import BLOCKCHAIN_CONFIG, LOGGING_CONFIG
from src.utils.logger import setup_logger   
from src.utils.middleware import log_requests
import datetime


config = BLOCKCHAIN_CONFIG
logger = setup_logger('api.routes') # TODO: set up logger for all routes 

# Creating a Flask Blueprint for routing
routes = Blueprint('routes', __name__)

# Creating a Blockchain object
blockchain = Blockchain()


# Mine a block
@routes.route('/mine_block', methods=['POST'])
@log_requests
def mine_block() -> Tuple[Response, int]:
    logger.info("Processing mine_block request")
    try:
        # getting miner info:
        request_data: Optional[Dict[str, Any]] = request.get_json()
        logger.info(f'Received request data')
        if not request_data or 'miner_address' not in request_data:
            message: str = 'Miner address is required to proceed'
            return make_response(message, 400)

        miner_address: str = request_data['miner_address']

        # mining process:
        logger.info(f'Mining block')
        prev_block: Dict[str, Any] = blockchain.get_prev_block()
        proof: int = blockchain.proof_of_work(prev_block['proof'])
        prev_hash: str = hash_block(prev_block)
        logger.info(f'Block mined successfully')

        # Add mining reward before creating new block
        logger.info(f'Adding mining reward')
        total_gas: float = sum(transaction['gas'] for transaction in blockchain.mempool)
        blockchain.add_transaction(sender='0', receiver=miner_address, amount=config['BLOCK_REWARD'] + total_gas)
        logger.info(f'Mining reward added successfully')

        # Create the block with updated mempool including mining reward
        logger.info(f'Creating block')
        block: Dict[str, Any] = blockchain.create_block(proof, prev_hash)
        logger.info(f'Block created successfully')

        message: str = 'Congratulations on mining a block!'
        data: Dict[str, Any] = block
        logger.info(f'Saving chain')
        blockchain.save_chain()
        logger.info(f'Chain saved successfully')
        logger.info(f"Block {block['index']} mined successfully")
        return make_response(message, 200, data)
    except Exception as e:
        logger.error(f"Error mining block: {str(e)}")
        return make_response(f"Error mining block: {str(e)}", 500)


# Registering a node
@routes.route('/register_node', methods=['POST'])
@log_requests
def register_node() -> Tuple[Response, int]:
    logger.info("Processing register_node request")
    try:
        request_data: Optional[Dict[str, Any]] = request.get_json()
        nodes: Optional[List[str]] = request_data.get('nodes')
        if nodes is None:
            logger.warning("Register node request received with no nodes")
            message: str = 'No nodes provided'
            response: Tuple[Response, int] = make_response(message, 400)
        else:
            logger.info(f"Registering {len(nodes)} new nodes")
            for node in nodes:
                blockchain.add_node(node)
            message: str = f'{len(blockchain.nodes)} Nodes have been added to the network'
            data: Dict[str, List[str]] = {
                'total_nodes': list(blockchain.nodes)
            }
            logger.info(f"Successfully registered {len(nodes)} nodes")
            response: Tuple[Response, int] = make_response(message, 201, data)
        blockchain.save_chain()
        logger.info("Node registration response sent")
        return response
    except Exception as e:
        logger.error(f"Error registering nodes: {str(e)}")
        return make_response(f'Error while registering nodes: {str(e)}', 500)


# Getting the full blockchain
@routes.route('/get_chain', methods=['GET'])
@log_requests
def get_chain() -> Tuple[Response, int]:
    try:
        logger.info("Processing get_chain request")
        message: str = 'Blockchain length fetch successful'
        data: Dict[str, Any] = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain)
        }
        logger.info(f"Returning chain with length {len(blockchain.chain)}")
        response: Tuple[Response, int] = make_response(message, 200, data)
        blockchain.save_chain()
        logger.info("Chain response sent")
        return response
    except Exception as e:
        logger.error(f"Error getting chain: {str(e)}")
        return make_response(f'Error while getting chain: {str(e)}', 500)


# Replace the chain with the longest one among peers
@routes.route('/replace_chain', methods=['POST'])
@log_requests
def replace_chain() -> Tuple[Response, int]:
    try:
        logger.info("Processing replace_chain request")
        is_replaced: bool = blockchain.replace_chain()
        logger.info(f"Chain replacement {'successful' if is_replaced else 'not needed'}")
        message: str = f'The chain {"was replaced by" if is_replaced else "is already"} the longest one'
        data: Dict[str, Any] = {
            'is_replaced': is_replaced,
            'chain': blockchain.chain
        }
        response: Tuple[Response, int] = make_response(message, 200, data)
        blockchain.save_chain()
        logger.info("Chain replacement response sent")
        return response
    except Exception as e:
        logger.error(f"Error replacing chain: {str(e)}")
        return make_response(f'Error while replacing chain: {str(e)}', 500)


# Check if blockchain is valid
@routes.route('/is_valid', methods=['GET'])
@log_requests
def is_valid() -> Tuple[Response, int]:
    try:
        logger.info("Processing is_valid request")
        valid: bool = blockchain.is_chain_valid()
        message: str = 'Blockchain validity check completed'
        data: Dict[str, bool] = {
            'is_valid': valid
        }
        response: Tuple[Response, int] = make_response(message, 200, data)
        blockchain.save_chain()
        logger.info(f"Blockchain validity check completed: {'valid' if valid else 'invalid'}")
        return response
    except Exception as e:
        logger.error(f"Error checking chain validity: {str(e)}")
        return make_response(f'Error while checking chain validity: {str(e)}', 500)


# Get a user's balance
@routes.route('/get_balance/<user>', methods=['GET'])
@log_requests
def get_user_balance(user: str) -> Tuple[Response, int]:
    try:
        if not user:
            logger.error("No user provided for balance check")
            return make_response("User parameter is required", 400)
            
        logger.info(f"Processing get_user_balance request for user {user}")
        balance: float = blockchain.get_user_balance(user)
        message: str = f'Fetched {user}\'s balance successfully'
        data: Dict[str, Any] = {
            'user': user,
            'balance': balance
        }
        response: Tuple[Response, int] = make_response(message, 200, data)
        blockchain.save_chain()
        logger.info(f"Fetched {user}\'s balance successfully")
        return response
    except Exception as e:
        logger.error(f"Error getting user balance: {str(e)}")
        return make_response(f'Error while getting user balance: {str(e)}', 500)


# Load the blockchain from persistent storage
@routes.route('/load_chain', methods=['GET'])
@log_requests
def load_chain() -> Tuple[Response, int]:
    try:
        logger.info("Processing load_chain request")
        result: bool = blockchain.load_chain()
        if result:
            message: str = f'Blockchain loaded from memory'
            response: Tuple[Response, int] = make_response(message, 200)
            logger.info("Blockchain loaded successfully")
        else:
            logger.error("Error loading blockchain from memory, starting fresh.")
            message: str = f'Error loading blockchain from memory, starting fresh.'
            response: Tuple[Response, int] = make_response(message, 400)
        blockchain.save_chain()
        logger.info("Blockchain initiated successfully")
        return response
    except Exception as e:
        logger.error(f"Error loading chain: {str(e)}")
        return make_response(f'Error while loading chain: {str(e)}', 500)


# Add transaction to the memory pool, to await mining
@routes.route('/add_transaction', methods=['POST'])
@log_requests
def add_transaction() -> Tuple[Response, int]:
    try:
        logger.info("Processing add_transaction request")
        request_data: Optional[Dict[str, Any]] = request.get_json()
        if not request_data:
            logger.error("No request data provided")
            return make_response("Request data is required", 400)

        required_fields: List[str] = ['sender', 'receiver', 'amount']
        err: Optional[str] = validate_fields(request_data, required_fields)
        if err:
            logger.error(f"Validation error: {err}")
            response: Tuple[Response, int] = make_response(err, 400)
        else:
            index: int = blockchain.add_transaction(
                sender=request_data['sender'],
                receiver=request_data['receiver'],
                amount=request_data['amount']
            )
            message: str = f'Transaction will be added in block {index}'
            response: Tuple[Response, int] = make_response(message, 201)
            blockchain.save_chain()
            logger.info(f"Transaction added to block {index}")
        return response
    except Exception as e:
        logger.error(f"Error adding transaction: {str(e)}")
        return make_response(f'Error while adding transaction: {str(e)}', 500)


# Broadcast a transaction amongst peers
@routes.route('/broadcast_transaction', methods=['POST'])
@log_requests
def broadcast_transaction() -> Tuple[Response, int]:
    # TODO: find if this is needed or can be merged with add_transaction
    try:
        logger.info("Processing broadcast_transaction request")
        request_data: Optional[Dict[str, Any]] = request.get_json()
        if not request_data:
            logger.error("No request data provided")
            return make_response("Request data is required", 400)

        required_fields: List[str] = ['sender', 'receiver', 'amount']
        err: Optional[str] = validate_fields(request_data, required_fields)
        if err:
            logger.error(f"Validation error: {err}")
            response: Tuple[Response, int] = make_response(err, 400)
        else:
            index: Optional[int] = blockchain.add_transaction(
                sender=request_data['sender'],
                receiver=request_data['receiver'],
                amount=request_data['amount']
            )
            if index:
                message: str = f'Transaction will be added to block {index}'
                response: Tuple[Response, int] = make_response(message, 201)
                logger.info(f"Transaction broadcast successful for block {index}")
            else:
                message: str = 'Transaction failed'
                response: Tuple[Response, int] = make_response(message, 400)
                logger.error("Transaction broadcast failed")
        blockchain.save_chain()
        return response
    except Exception as e:
        logger.error(f"Error broadcasting transaction: {str(e)}")
        return make_response(f'Error while broadcasting transaction: {str(e)}', 500)


@routes.route('/health', methods=['GET'])
@log_requests
def health_check() -> Tuple[Response, int]:
    try:
        logger.debug("Health check requested")
        message: str = "Service is healthy"
        data: Dict[str, str] = {
            'status': 'healthy',
            'timestamp': str(datetime.datetime.now())
        }
        logger.info("Health check completed successfully")
        return make_response(message, 200, data)
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        return make_response(f'Error during health check: {str(e)}', 500)


@routes.route('/deploy_contract', methods=['POST'])
@log_requests
def deploy_contract() -> Tuple[Response, int]:
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        required_fields: List[str] = ['code', 'owner']
        if err := validate_fields(data, required_fields):
            return make_response(err, 400)
            
        contract_address: str = blockchain.deploy_contract(
            code=data['code'],
            owner=data['owner']
        )
        message: str = 'Contract deployed successfully'
        data: Dict[str, str] = {
            'contract_address': contract_address
        }
        return make_response(message, 201, data)
    except Exception as e:

        return make_response(f'Error deploying contract: {str(e)}', 500)

@routes.route('/execute_contract/<contract_address>', methods=['POST'])
@log_requests
def execute_contract(contract_address: str) -> Tuple[Response, int]:
    try:
        params: Dict[str, Any] = request.get_json() or {}
        result: Dict[str, Any] = blockchain.execute_smart_contract(contract_address, params)
        message: str = 'Contract executed successfully'
        data: Dict[str, Any] = {
            'result': result
        }
        return make_response(message, 201, data)
    except Exception as e:
        message: str = f'Error executing contract: {str(e)}'
        data: Dict[str, Any] = {
            'result': result
        }
        return make_response(message, 500, data)



