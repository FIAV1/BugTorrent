#!/usr/bin/env python


def count_set_bits(n: int) -> int:
	""" Brian Kernighan’s Algorithm:
	When we do bitwise (number) & (number-1), right most SET bit of "number" will be unset.
	:param n: the
	:return: int - the number of set bits in the number given
	"""
	count = 0
	while n:
		n &= (n - 1)
		count += 1
	return count
