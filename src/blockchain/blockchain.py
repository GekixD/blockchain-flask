import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse
from src.utils.logger import setup_logger
from src.config.config import BLOCKCHAIN_CONFIG
from src.blockchain.helpers import hash_block

config = BLOCKCHAIN_CONFIG
logger = setup_logger('blockchain.core')

# Building a Blockchain
class Blockchain:

    def __init__(self):
        logger.info("Initializing new blockchain")
        self.chain = []
        self.mempool = []
        self.processed_transactions = set()
        self.nodes = set()
        self.create_block(proof=1, prev_hash='0' * config['DIFFICULTY'])
        self.gas_fee = config['GAS_FEE']

    def save_chain(self, filename=config['CHAIN_FILE']):
        try:
            with open(filename, 'w') as file:
                state = {
                    'chain': self.chain,
                    'nodes': list(self.nodes),
                    'mempool': self.mempool,
                    'processed_transactions': list(self.processed_transactions)
                }
                json.dump(state, file)
                logger.info(f"Chain saved successfully to {filename}")
        except Exception as e:
            logger.error(f"Error saving chain: {str(e)}")
            raise

    def load_chain(self, filename=config['CHAIN_FILE']):
        try:
            with open(filename, 'r') as file:
                state = json.load(file)
                self.chain = state['chain']
                self.mempool = state['mempool']
                self.processed_transactions = set(state['processed_transactions '])
                self.nodes = set(state['nodes'])
                logger.info(f"Chain loaded successfully from {filename}")
                return True
        except FileNotFoundError:
            logger.warning('Nonexistent blockchain.')
            return False

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        logger.info(f"Added new node: {parsed_url.netloc}")

    def replace_chain(self):
        longest_chain = None
        max_len = len(self.chain)

        for node in self.nodes:
            try:
                response = requests.get(f'http://{node}/get_chain', timeout=config['NODE_TIMEOUT'])
                if response.status_code == 200:
                    node_chain = response.json()['chain']
                    node_length = response.json()['length']
                    if node_length > max_len and self.is_chain_valid(node_chain):
                        max_len = node_length
                        longest_chain = node_chain
                if longest_chain:
                    self.chain = longest_chain
                    logger.info(f"Chain replaced with longer chain from node {node}")
                    return True
            except requests.exceptions.RequestException:
                logger.error(f"Failed to connect to node {node}")
                continue
        logger.info("Chain replacement not needed - current chain is longest")
        return False

    def create_block(self, proof, prev_hash):
        logger.info(f"Creating new block with proof: {proof}")
        try:
            block = {
                'index': len(self.chain) + 1,
                'timestamp': str(datetime.datetime.now()),
                'transactions': self.mempool,
                'proof': proof,
                'prev_hash': prev_hash
            }
            self.mempool = []
            self.chain.append(block)
            logger.info(f"Block {block['index']} created successfully")
            return block
        except Exception as e:
            logger.error(f"Error creating block: {str(e)}")
            raise

    def get_prev_block(self):
        logger.debug("Getting previous block")
        return self.chain[-1]

    def get_user_balance(self, user):
        balance = 0
        for block in self.chain:
            for transaction in block.get('transactions', []):
                if transaction['sender'] == user:
                    balance -= transaction['amount'] + transaction['gas']
                elif transaction['receiver'] == user:
                    balance += transaction['amount']
        logger.info(f"Calculated balance for user {user}: {balance}")
        return balance

    def add_transaction(self, sender, receiver, amount):
        if amount <= 0:
            logger.error("Invalid transaction: amount must be positive")
            raise ValueError('Transaction amount must be positive')
        if sender != '0':  # user 0 is the system mining rewards, thus no balance check and gas fee isn't applied
            sender_balance = self.get_user_balance(sender)
            if sender_balance < amount * (1 + self.gas_fee):
                logger.warning(f"Transaction failed: insufficient balance for user {sender}")
                return False
        transaction = {'sender': sender, 'receiver': receiver, 'amount': amount, 'gas': amount * self.gas_fee * (sender != '0')}
        transaction_hash = hashlib.sha256(json.dumps(transaction, sort_keys=True).encode()).hexdigest()
        if transaction_hash in self.processed_transactions:
            logger.warning(f"Transaction {transaction_hash} already processed")
            return False
        self.mempool.append(transaction)
        self.processed_transactions.add(transaction_hash)
        self.broadcast_transaction(transaction)
        logger.info(f"Added transaction: {sender} -> {receiver}, amount: {amount}")
        return self.get_prev_block()['index'] + 1

    def broadcast_transaction(self, transaction):
        for node in self.nodes:
            try:
                response = requests.post(f'http://{node}/add_transaction', json=transaction, timeout=config['NODE_TIMEOUT'])
                if response.status_code != 201:
                    logger.error(f'Failed to broadcast transaction to node: {node}')
            except requests.exceptions.RequestException:
                logger.error(f'Could not connect to node: {node}')

    def proof_of_work(self, prev_proof=None, difficulty=config['DIFFICULTY']):
        logger.info("Starting proof of work calculation")
        # TODO: Implement a method to adjust the difficulty based on average mining time
        if prev_proof is None:
            prev_proof = self.get_prev_block()['proof']
        new_proof = 1
        target = '0' * difficulty
        while True:
            # TODO: make a better PoW proof for mining (see hashing.py)
            hash_operation = hashlib.sha256(str((new_proof ** 2) - (prev_proof ** 2)).encode()).hexdigest()
            if hash_operation[:difficulty] == target:
                logger.info(f"Found proof of work: {new_proof}")
                return new_proof
            new_proof += 1

    def is_chain_valid(self, chain=None):
        logger.info("Validating blockchain")
        if chain is None:
            chain = self.chain
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != hash_block(prev_block):
                logger.error(f"Invalid chain: hash mismatch at block {block_index}")
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str((proof ** 2) - (prev_proof ** 2)).encode()).hexdigest()
            if hash_operation[:config['DIFFICULTY']] != '0' * config['DIFFICULTY']:
                logger.error(f"Invalid chain: proof of work invalid at block {block_index}")
                return False
            prev_block = chain[block_index]
            block_index += 1
        logger.info("Chain validation successful")
        return True

    def execute_smart_contract(self, contract_code, params):
        try:
            logger.info("Executing smart contract")
            exec(contract_code, {}, params)
            result = params.get('result', None)
            logger.info(f"Smart contract execution completed with result: {result}")
            return result
        except Exception as e:
            logger.error(f'Error while executing smart contract: {e}')
            return None
