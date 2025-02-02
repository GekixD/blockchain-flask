import unittest
import json
from src.api.app import app

class TestBlockchainAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_chain(self):
        response = self.app.get('/get_chain')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('chain', data)
        self.assertIn('length', data)

    def test_mine_block(self):
        response = self.app.post('/mine_block',
                               json={'miner_address': 'test_miner'},
                               content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('index', data)
        self.assertIn('timestamp', data)
        self.assertIn('proof', data) 