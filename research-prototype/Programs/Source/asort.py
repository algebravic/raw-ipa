"""
New radix sort, using multiple bits.

This was derived from the files sorting.py
in the MP-SPDZ Compiler directory.

The radix sort has 3 phases:
1) Break up the keys into bit matrices.
   Optionally treat signed data (if specified)
2) The counting phase.  This is done prefix sum applied
   to various bit values derived from the keys
3) The counting phase produces a permutation to be applied,
   which is performed by randomizing it with a secure shuffle,
   then revealing it so that the parties may actually
   rearrange, and the unshuffling with the secure shuffle.

The secure shuffle is relatively expensive compared with the
multiplication protocol, so that by treating multiple bit
values we may reduce the number of secure shuffles at the expense
of more secure multiples.  The best trade-off appears to be
for either 3 or 4 bit fields, but will depend on the protocol
used since the relative costs will vary.
"""
from Compiler import types
from single import bit_radix_sort
from double import double_bit_radix_sort
from triple import triple_bit_radix_sort
from quadruple import quadruple_bit_radix_sort

def radix_sort(arr, D, n_bits = None, signed = False, chunk = 1):
    assert len(arr) == len(D)
    bs = types.Matrix.create_from(
        arr.get_vector().bit_decompose(n_bits))
    if signed and len(bs) > 1:
        bs[-1][:] = bs[-1][:].bit_not()

    sorters = {1: bit_radix_sort,
               2: double_bit_radix_sort,
               3: triple_bit_radix_sort,
               4: quadruple_bit_radix_sort}

    if chunk not in sorters:
        raise ValueError("Illegal chunk value")

    sorters[chunk](bs, D)
