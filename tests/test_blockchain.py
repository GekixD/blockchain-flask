import unittest
from src.blockchain.blockchain import Blockchain
from src.config.config import BLOCKCHAIN_CONFIG

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain()

    def test_create_block(self):
        initial_length = len(self.blockchain.chain)
        block = self.blockchain.create_block(proof=100, prev_hash='test_hash')
        
        self.assertEqual(len(self.blockchain.chain), initial_length + 1)
        self.assertEqual(block['prev_hash'], 'test_hash')
        self.assertEqual(block['proof'], 100)
        self.assertEqual(block['index'], initial_length + 1)

    def test_get_prev_block(self):
        block = self.blockchain.get_prev_block()
        self.assertEqual(block, self.blockchain.chain[-1])

    def test_add_transaction(self):
        # Test mining reward transaction
        result = self.blockchain.add_transaction('0', 'miner1', 10)
        self.assertIsNotNone(result)
        
        # Test normal transaction
        result = self.blockchain.add_transaction('user1', 'user2', 5)
        self.assertIsNotNone(result)
        
        # Test invalid amount
        with self.assertRaises(ValueError):
            self.blockchain.add_transaction('user1', 'user2', -5) 