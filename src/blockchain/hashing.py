from sympy import prime
from functools import reduce
from typing import List
from src.config.config import BLOCKCHAIN_CONFIG

config = BLOCKCHAIN_CONFIG['HASH_CONFIG']


def get_dynamic_primes(s: str) -> List[int]:
    n = len(s) ** config.get('size_exponent', 5) % config.get('prime_limit', 9999999)
    if n == 0:
        return [2]
    return [prime(n//(i+1)) for i in range(config.get('primes_no', 1))]


def get_ord_sum(s: str) -> int:
    return sum(ord(c) * (i+1) for i, c in enumerate(s))


def mix_value(v: int, p: int, mix_sum: int) -> int:
    return (v * p + mix_sum) ^ (v >> config.get('mix_shift', 3))


def calculate_hash(primes: List[int], n: int) -> int:
    return reduce(lambda acc, p: int(bin(mix_value(acc, p, n))[2:], 10) % p, primes * config.get('mix_rounds', 1), n)


def standardize_hash_value(value: int) -> str:
    return hex(value)[2:].zfill(config.get('hash_size', 256))[:config.get('hash_size', 256)]


def hashing_algorithm(input_string: str) -> str:
    return standardize_hash_value(calculate_hash(get_dynamic_primes(input_string), get_ord_sum(input_string)))
