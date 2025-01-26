import logging

LOGGING_CONFIG = {
    'LOG_LEVEL': logging.INFO,
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_DIR': 'logs',
    'MAX_LOG_SIZE': 10 * 1024 * 1024,
    'BACKUP_COUNT': 5,
    'COMPONENTS': {
        'blockchain': {
            'level': logging.INFO,
            'filename': 'blockchain.log'
        },
        'api': {
            'level': logging.INFO,
            'filename': 'api.log'
        },
        'server': {
            'level': logging.INFO,
            'filename': 'server.log'
        }
    }
}

BLOCKCHAIN_CONFIG = {
    # Mining settings
    'DIFFICULTY': 4,
    'BLOCK_REWARD': 1.0,
    'GAS_FEE': 0.01,
    'TARGET_BLOCK_TIME': 600,
    
    # Network settings
    'SYNC_INTERVAL': 60,
    'NODE_TIMEOUT': 5,
    
    # Storage settings
    'CHAIN_FILE': 'blockchain.json',
    
    # Hashing settings
    'HASH_CONFIG': {
        'Size_exponent': 5,
        'primes_no': 2,
        'prime_limit': 9999999,
        'hash_size': 16,
        'mix_shift': 3,
        'mix_rounds': 5
    }
}