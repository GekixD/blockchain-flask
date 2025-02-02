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
        if not request_data or 'miner_address' not in request_data:
            message = 'Miner address is required to proceed'
            return make_response(message, 400)

        miner_address = request_data['miner_address']

        # mining process:
        prev_block = blockchain.get_prev_block()
        proof = blockchain.proof_of_work(prev_block['proof'])
        prev_hash = hash_block(prev_block)
        
        # Add mining reward before creating new block
        total_gas = sum(transaction['gas'] for transaction in blockchain.mempool)
        blockchain.add_transaction(sender='0', receiver=miner_address, amount=config['BLOCK_REWARD'] + total_gas)
        
        # Create the block with updated mempool including mining reward
        block = blockchain.create_block(proof, prev_hash)

        message = 'Congratulations on mining a block!'
        data = block
        
        blockchain.save_chain()
        logger.info(f"Block {block['index']} mined successfully")
        return make_response(message, 200, data)
    except Exception as e:
        logger.error(f"Error mining block: {str(e)}")
        return make_response(f'Error while mining block: {str(e)}', 500)


# Registering a node
@routes.route('/register_node', methods=['POST'])
def register_node():
    request_data = request.get_json()
    nodes = request_data.get('nodes')
    if nodes is None:
        message = 'No nodes provided'
        response = make_response(message, 400)
    else:
        for node in nodes:
            blockchain.add_node(node)
        message = f'{len(blockchain.nodes)} Nodes have been added to the network'
        data = {
            'total_nodes': list(blockchain.nodes)
        }
        response = make_response(message, 201, data)
    blockchain.save_chain()
    return response


# Getting the full blockchain
@routes.route('/get_chain', methods=['GET'])
def get_chain():
    message = 'Blockchain length fetch successful'
    data = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    response = make_response(message, 200, data)
    blockchain.save_chain()
    return response


# Replace the chain with the longest one among peers
@routes.route('/replace_chain', methods=['POST'])
def replace_chain():
    is_replaced = blockchain.replace_chain()
    message = f'The chain {"was replaced by" if is_replaced else "is already"} the longest one',
    data = {
        'is_replaced': is_replaced,
        'chain': blockchain.chain
    }
    response = make_response(message, 200, data)
    blockchain.save_chain()
    return response


# Check if blockchain is valid
@routes.route('/is_valid', methods=['GET'])
def is_valid():
    valid = blockchain.is_chain_valid()
    message = 'Blockchain validity check completed'
    data = {
        'is_valid': valid
    }
    response = make_response(message, 200, data)
    blockchain.save_chain()
    return response


# Get a user's balance
@routes.route('/get_balance/<user>', methods=['GET'])
def get_user_balance(user):
    balance = blockchain.get_user_balance(user)
    message = f'Fetched {user}\'s balance successfully'
    data = {
        'user': user,
        'balance': balance
    }
    response = make_response(message, 200, data)
    blockchain.save_chain()
    return response


# Load the blockchain from persistent storage
@routes.route('/load_chain', methods=['GET'])
def load_chain():
    result = blockchain.load_chain()
    if result:
        message = f'Blockchain loaded from memory'
        response = make_response(message, 200)
    else:
        message = f'Error loading blockchain from memory, starting fresh.'
        response = make_response(message, 400)
    blockchain.save_chain()
    return response


# Add transaction to the memory pool, to await mining
@routes.route('/add_transaction', methods=['POST'])
def add_transaction():
    request_data = request.get_json()
    required_fields = ['sender', 'receiver', 'amount']
    err = validate_fields(request_data, required_fields)
    if err:
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
    return response


# Broadcast a transaction amongst peers
@routes.route('/broadcast_transaction', methods=['POST'])
def broadcast_transaction():
    # TODO: find if broadcast transaction endpoint is really needed or can be merged with add_transaction
    request_data = request.get_json()
    required_fields = ['sender', 'receiver', 'amount']
    err = validate_fields(request_data, required_fields)
    if err:
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
        else:
            message = 'Transaction failed'
            response = make_response(message, 400)
    blockchain.save_chain()
    return response


@routes.route('/health', methods=['GET'])
@log_requests
def health_check():
    logger.debug("Health check requested")
    message = "Service is healthy"
    data = {
        'status': 'healthy',
        'timestamp': str(datetime.datetime.now())
    }
    return make_response(message, 200, data)

