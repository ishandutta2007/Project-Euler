'''
@Author: zhaoyang.liang
@Github: https://github.com/LzyRapx
@Date: 2020-02-04 00:16:33
'''
#coding: utf-8

"""
prime-related functions:
    _primes_list(n): Returns a array of primes, 2 <= p < n
    _is_prime(p, accuracy=100): Miller-Rabin primality test
                                details see: https://en.wikipedia.org/wiki/Miller-Rabin_primality_test
    _mobius_list(n): return mobius function mu(k) for 0 <= k <= n
    _pollard_rho(n, rand=True): return a non-trivial(not one or n) factor of n
                                Pollard rho prime factorization algorithm
                                details see: https://en.wikipedia.org/wiki/Pollard's_rho_algorithm
    prime_divisor_decomposition(n, rand=True):
                                Prime factor decomposition
                                writing n as a product of prime factors. To factorise a number, 
                                divide it by the first possible prime number.
    all_divisors(n, rand=False): return all divisors of n as a sorted list
"""
import random
import numpy as np

from base import cprod, gcd, sqrt, isqrt

try:
    from gmpy2 import is_prime
except:
    is_prime = None

primes_list = None
mobius_list = None
factor_sieve = None

def _primes_list(n): # n >= 6
    """input n>=6, Returns a array of primes, 2 <= p < n"""

    sieve = np.ones(n//3 + (n % 6 == 2), dtype=np.bool)
    for i in range(1, int(sqrt(n))//3+1):
        if sieve[i]:
            k = (3 * i + 1) | 1
            sieve[k*k//3::2*k] = False
            sieve[k*(k - 2*(i & 1) + 4)//3::2*k] = False
    plist = np.r_[2, 3, ((3 * np.nonzero(sieve)[0][1:] + 1) | 1)]
    return [int(x) for x in plist]

if primes_list is None:
    primes_list = _primes_list

def _mr_decompose(n):
    exponentOfTwo = 0
    while n % 2 == 0:
        n //= 2
        exponentOfTwo += 1
    return exponentOfTwo, n

def _mr_isWitness(possibleWitness, p, exponent, remainder):
    possibleWitness = pow(possibleWitness, remainder, p)
    if possibleWitness == 1 or possibleWitness == p - 1:
        return False
    for _ in range(exponent):
        possibleWitness = pow(possibleWitness, 2, p)
        if possibleWitness == p - 1:
            return False
    return True

def _is_prime(p, accuracy=100):
    """
    Miller-Rabin primality test
    https://en.wikipedia.org/wiki/Miller-Rabin_primality_test
    """

    if p < 2:
        return False
    if p == 2 or p == 3:
        return True
    
    exponent, remainder = _mr_decompose(p - 1)

    for _ in range(accuracy):
        possibleWitness = random.randint(2, p - 2)
        if _mr_isWitness(possibleWitness, p, exponent, remainder):
            return False
    return True

if is_prime is None:
    is_prime = _is_prime

def _mobius_list(n):
    """return mobius function mu(k) for 0 <= k <= n"""

    plist = primes_list(isqrt(n)+1)
    mlist = np.ones(n+1, dtype=np.int64)

    for p in plist:
        mlist[::p] *= -p
        mlist[::p*p] = 0

    for i in range(1, n+1):
        if mlist[i]:
            if abs(mlist[i]) < i:
                mlist[i] *= -1

            if mlist[i] > 0:
                mlist[i] = 1
            else:
                mlist[i] = -1
    return mlist

if mobius_list is None:
    mobius_list = _mobius_list

def _pollard_rho(n, rand=True):
    """
    return a non-trivial(not one or n) factor of n.
    Pollard rho prime factorization algorithm
    https://en.wikipedia.org/wiki/Pollard's_rho_algorithm
    """

    f = lambda x, c: x*x + c
    if not rand:
        x, c = 1, 1
    else:
        x, c = random.randrange(2, 1e6), random.randrange(2, 1e6)

    y, d = x, 1
    while d == 1 and d != n:
        x = f(x, c) % n
        y = f(y, c) % n
        y = f(y, c) % n
        d = gcd(y-x, n)
    return int(d)

P10K = primes_list(10000)
P10Kset = set(P10K)
def prime_divisor_decomposition(n, rand=True):
    dlist, clist = [], []

    # 奇偶性判断
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    if c:
        dlist.append(2)
        clist.append(c)

    # 首先用10000以内的小素数试除
    for p in iter(P10K):
        c = 0
        while n % p == 0:
            n //= p
            c += 1
        if c:
            dlist.append(p)
            clist.append(c)

        if n == 1:
            return list(zip(dlist, clist))

        if n in P10Kset:  # set的in操作复杂度<=O(log(n))
            dlist.append(n)
            clist.append(1)
            return list(zip(dlist, clist))

        n = int(n)

    # 然后用Pollard rho方法生成素因子
    while 1:
        if n == 1:
            return list(zip(dlist, clist))

        if is_prime(n):
            dlist.append(n)
            clist.append(1)
            return list(zip(dlist, clist))

        p = _pollard_rho(n, rand)
        c = 0
        while n % p == 0:
            n //= p
            c += 1
        dlist.append(p)
        clist.append(c)

        n = int(n)

def all_divisors(n, rand=False):
    if n == 1:
        return [1]

    primefactors = prime_divisor_decomposition(n, rand)
    d = len(primefactors)
    clist = [0] * d
    output = []
    while 1:
        output.append(cprod([primefactors[i][0]**clist[i] for i in range(d)]))
        k = 0
        while 1:
            clist[k] += 1
            if clist[k] <= primefactors[k][1]:
                break
            clist[k] = 0
            k += 1
            if k >= d:
                return sorted(output)