from flask import request, Blueprint
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
def mine_block():
    logger.info("Processing mine_block request")
    try:
        # getting miner info:
        request_data = request.get_json()
        logger.info(f'Received request data')
        if not request_data or 'miner_address' not in request_data:
            message = 'Miner address is required to proceed'
            return make_response(message, 400)

        miner_address = request_data['miner_address']

        # mining process:
        logger.info(f'Mining block')
        prev_block = blockchain.get_prev_block()
        proof = blockchain.proof_of_work(prev_block['proof'])
        prev_hash = hash_block(prev_block)
        logger.info(f'Block mined successfully')

        # Add mining reward before creating new block
        logger.info(f'Adding mining reward')
        total_gas = sum(transaction['gas'] for transaction in blockchain.mempool)
        blockchain.add_transaction(sender='0', receiver=miner_address, amount=config['BLOCK_REWARD'] + total_gas)
        logger.info(f'Mining reward added successfully')

        # Create the block with updated mempool including mining reward
        logger.info(f'Creating block')
        block = blockchain.create_block(proof, prev_hash)
        logger.info(f'Block created successfully')

        message = 'Congratulations on mining a block!'
        data = block
        logger.info(f'Saving chain')
        blockchain.save_chain()
        logger.info(f'Chain saved successfully')
        logger.info(f"Block {block['index']} mined successfully")
        return make_response(message, 200, data)
    except Exception as e:
        logger.error(f"Error mining block: {str(e)}")
        return make_response(f'Error while mining block: {str(e)}', 500)


# Registering a node
@routes.route('/register_node', methods=['POST'])
@log_requests
def register_node():
    logger.info("Processing register_node request")
    try:
        request_data = request.get_json()
        nodes = request_data.get('nodes')
        if nodes is None:
            logger.warning("Register node request received with no nodes")
            message = 'No nodes provided'
            response = make_response(message, 400)
        else:
            logger.info(f"Registering {len(nodes)} new nodes")
            for node in nodes:
                blockchain.add_node(node)
            message = f'{len(blockchain.nodes)} Nodes have been added to the network'
            data = {
                'total_nodes': list(blockchain.nodes)
            }
            logger.info(f"Successfully registered {len(nodes)} nodes")
            response = make_response(message, 201, data)
        blockchain.save_chain()
        logger.info("Node registration response sent")
        return response
    except Exception as e:
        logger.error(f"Error registering nodes: {str(e)}")
        return make_response(f'Error while registering nodes: {str(e)}', 500)


# Getting the full blockchain
@routes.route('/get_chain', methods=['GET'])
@log_requests
def get_chain():
    try:
        logger.info("Processing get_chain request")
        message = 'Blockchain length fetch successful'
        data = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain)
        }
        logger.info(f"Returning chain with length {len(blockchain.chain)}")
        response = make_response(message, 200, data)
        blockchain.save_chain()
        logger.info("Chain response sent")
        return response
    except Exception as e:
        logger.error(f"Error getting chain: {str(e)}")
        return make_response(f'Error while getting chain: {str(e)}', 500)


# Replace the chain with the longest one among peers
@routes.route('/replace_chain', methods=['POST'])
@log_requests
def replace_chain():
    try:
        logger.info("Processing replace_chain request")
        is_replaced = blockchain.replace_chain()
        logger.info(f"Chain replacement {'successful' if is_replaced else 'not needed'}")
        message = f'The chain {"was replaced by" if is_replaced else "is already"} the longest one'
        data = {
            'is_replaced': is_replaced,
            'chain': blockchain.chain
        }
        response = make_response(message, 200, data)
        blockchain.save_chain()
        logger.info("Chain replacement response sent")
        return response
    except Exception as e:
        logger.error(f"Error replacing chain: {str(e)}")
        return make_response(f'Error while replacing chain: {str(e)}', 500)


# Check if blockchain is valid
@routes.route('/is_valid', methods=['GET'])
@log_requests
def is_valid():
    try:
        logger.info("Processing is_valid request")
        valid = blockchain.is_chain_valid()
        message = 'Blockchain validity check completed'
        data = {
            'is_valid': valid
        }
        response = make_response(message, 200, data)
        blockchain.save_chain()
        logger.info(f"Blockchain validity check completed: {'valid' if valid else 'invalid'}")
        return response
    except Exception as e:
        logger.error(f"Error checking chain validity: {str(e)}")
        return make_response(f'Error while checking chain validity: {str(e)}', 500)


# Get a user's balance
@routes.route('/get_balance/<user>', methods=['GET'])
@log_requests
def get_user_balance(user):
    try:
        if not user:
            logger.error("No user provided for balance check")
            return make_response("User parameter is required", 400)
            
        logger.info(f"Processing get_user_balance request for user {user}")
        balance = blockchain.get_user_balance(user)
        message = f'Fetched {user}\'s balance successfully'
        data = {
            'user': user,
            'balance': balance
        }
        response = make_response(message, 200, data)
        blockchain.save_chain()
        logger.info(f"Fetched {user}\'s balance successfully")
        return response
    except Exception as e:
        logger.error(f"Error getting user balance: {str(e)}")
        return make_response(f'Error while getting user balance: {str(e)}', 500)


# Load the blockchain from persistent storage
@routes.route('/load_chain', methods=['GET'])
@log_requests
def load_chain():
    try:
        logger.info("Processing load_chain request")
        result = blockchain.load_chain()
        if result:
            message = f'Blockchain loaded from memory'
            response = make_response(message, 200)
            logger.info("Blockchain loaded successfully")
        else:
            logger.error("Error loading blockchain from memory, starting fresh.")
            message = f'Error loading blockchain from memory, starting fresh.'
            response = make_response(message, 400)
        blockchain.save_chain()
        logger.info("Blockchain initiated successfully")
        return response
    except Exception as e:
        logger.error(f"Error loading chain: {str(e)}")
        return make_response(f'Error while loading chain: {str(e)}', 500)


# Add transaction to the memory pool, to await mining
@routes.route('/add_transaction', methods=['POST'])
@log_requests
def add_transaction():
    try:
        logger.info("Processing add_transaction request")
        request_data = request.get_json()
        if not request_data:
            logger.error("No request data provided")
            return make_response("Request data is required", 400)

        required_fields = ['sender', 'receiver', 'amount']
        err = validate_fields(request_data, required_fields)
        if err:
            logger.error(f"Validation error: {err}")
            response = make_response(err, 400)
        else:
            index = blockchain.add_transaction(
                sender=request_data['sender'],
                receiver=request_data['receiver'],
                amount=request_data['amount']
            )
            message = f'Transaction will be added in block {index}'
            response = make_response(message, 201)
            blockchain.save_chain()
            logger.info(f"Transaction added to block {index}")
        return response
    except Exception as e:
        logger.error(f"Error adding transaction: {str(e)}")
        return make_response(f'Error while adding transaction: {str(e)}', 500)


# Broadcast a transaction amongst peers
@routes.route('/broadcast_transaction', methods=['POST'])
@log_requests
def broadcast_transaction():
    # TODO: find if this is needed or can be merged with add_transaction
    try:
        logger.info("Processing broadcast_transaction request")
        request_data = request.get_json()
        if not request_data:
            logger.error("No request data provided")
            return make_response("Request data is required", 400)

        required_fields = ['sender', 'receiver', 'amount']
        err = validate_fields(request_data, required_fields)
        if err:
            logger.error(f"Validation error: {err}")
            response = make_response(err, 400)
        else:
            index = blockchain.add_transaction(
                sender=request_data['sender'],
                receiver=request_data['receiver'],
                amount=request_data['amount']
            )
            if index:
                message = f'Transaction will be added to block {index}'
                response = make_response(message, 201)
                logger.info(f"Transaction broadcast successful for block {index}")
            else:
                message = 'Transaction failed'
                response = make_response(message, 400)
                logger.error("Transaction broadcast failed")
        blockchain.save_chain()
        return response
    except Exception as e:
        logger.error(f"Error broadcasting transaction: {str(e)}")
        return make_response(f'Error while broadcasting transaction: {str(e)}', 500)


@routes.route('/health', methods=['GET'])
@log_requests
def health_check():
    try:
        logger.debug("Health check requested")
        message = "Service is healthy"
        data = {
            'status': 'healthy',
            'timestamp': str(datetime.datetime.now())
        }
        logger.info("Health check completed successfully")
        return make_response(message, 200, data)
    except Exception as e:
        logger.error(f"Error during health check: {str(e)}")
        return make_response(f'Error during health check: {str(e)}', 500)

