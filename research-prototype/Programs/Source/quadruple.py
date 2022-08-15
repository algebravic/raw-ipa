"""
Sort by 3 bits at a time
"""

from Compiler import types, library, instructions, sorting
from itertools import product
from single import dest_comp
from double import double_dest_comp
from triple import triple_dest_comp

def quadruple_dest_comp(col0, col1, col2, col3):

    num = len(col0)
    assert ((num == len(col1))
            and (num == len(col2))
            and (num == len(col3)))

    x01 = col0 * col1
    x02 = col0 * col2
    x03 = col0 * col3
    x12 = col1 * col2
    x13 = col1 * col3
    x23 = col2 * col3
    x012 = col0 * x12
    x013 = col0 * x13
    x023 = col0 * x23
    x123 = col1 * x23
    x0123 = col0 * x123

    cum = types.sint.Array(num * 16)

    cum.assign_vector(1 - col0 - col1 - col2 - col3
                      + x01 + x02 + x03 + x12 + x13 + x23
                      - x012 - x013 - x023 - x123 + x0123,
                      base = 0) #0000
    cum.assign_vector(col0 - x01 - x02 - x03
                      + x012 + x013 + x023
                      - x0123, base = num) #0001
    cum.assign_vector(col1 - x01 - x12 - x13
                      + x012 + x013 + x123
                      - x0123, base = 2 * num) #0010
    cum.assign_vector(x01 - x012 - x013
                      + x0123, base = 3 * num) #0011
    cum.assign_vector(col2 - x02 - x12 - x23
                      + x012 + x023 + x123
                      - x0123, base = 4 * num) #0100
    cum.assign_vector(x02 - x012 - x023
                      + x0123, base = 5 * num) #0101
    cum.assign_vector(x12 - x012 - x123
                      + x0123, base = 6 * num) #0110
    cum.assign_vector(x012 - x0123, base = 7 * num) #0111
    cum.assign_vector(col3 - x03 - x13 - x23
                      + x013 + x023 + x123
                      - x0123, base = 8 * num) #1000
    cum.assign_vector(x03 - x013 - x023
                      + x0123, base = 9 * num) #1001
    cum.assign_vector(x13 - x013 - x123
                      + x0123, base = 10 * num) #1010
    cum.assign_vector(x013 - x0123, base = 11 * num) #1011
    cum.assign_vector(x23 - x023 - x123 + x0123, base = 12 * num) #1100
    cum.assign_vector(x023 - x0123, base = 13 * num) #1101
    cum.assign_vector(x123 - x0123, base = 14 * num) #1110
    cum.assign_vector(x013, base = 15 * num) #1111

    @library.for_range(len(cum) - 1)
    def _(i):
        cum[i + 1] = cum[i + 1] + cum[i]

    cparts = [cum.get_vector(base = _ * num, size = num)
              for _ in range(16)]

    dest = (cparts[0]
            + col0 * (cparts[1] - cparts[0])
            + col1 * (cparts[2] - cparts[0])
            + col2 * (cparts[4] - cparts[0])
            + col3 * (cparts[8] - cparts[0])
            + x01 * (cparts[0] - cparts[1] - cparts[2] + cparts[3])
            + x02 * (cparts[0] - cparts[1] - cparts[4] + cparts[5])
            + x03 * (cparts[0] - cparts[1] - cparts[8] + cparts[9])
            + x12 * (cparts[0] - cparts[2] - cparts[4] + cparts[6])
            + x13 * (cparts[0] - cparts[2] - cparts[8] + cparts[10])
            + x23 * (cparts[0] - cparts[4] - cparts[8] + cparts[12])
            # Fix the weight 3
            + x012 * (- cparts[0] + cparts[1] + cparts[2] + cparts[4]
                      - cparts[3] - cparts[5] - cparts[6]
                      + cparts[7] )
            + x013 * (- cparts[0] + cparts[1] + cparts[2] + cparts[8]
                      - cparts[3] - cparts[9] - cparts[10]
                      + cparts[11])
            + x023 * (- cparts[0] + cparts[1] + cparts[4] + cparts[8]
                      - cparts[5] - cparts[9] - cparts[12]
                      + cparts[13])
            + x123 * (- cparts[0] + cparts[2] + cparts[4] + cparts[8]
                      - cparts[6] - cparts[10] - cparts[12]
                      + cparts[14])
            + x0123 * (cparts[0]
                       - cparts[1] - cparts[2] - cparts[4] - cparts[8]
                       + cparts[3] + cparts[5] + cparts[6] + cparts[10] + cparts[12]
                       - cparts[7] - cparts[11] - cparts[13] - cparts[14]
                       + cparts[15])

            )
    return dest - 1

def quadruple_bit_radix_sort(bs, D):
    """
    Four bits at a time
     """
    n_bits, num = bs.sizes
    h = types.Array.create_from(types.sint(types.regint.inc(num)))
    # Test if n_bits is odd
    @library.for_range(n_bits // 4)
    def _(i):
        perm = quadruple_dest_comp(bs[4 * i].get_vector(),
                                   bs[4 * i + 1].get_vector(),
                                   bs[4 * i + 2].get_vector(),
                                   bs[4 * i + 3].get_vector())

        sorting.reveal_sort(perm, h, reverse = False)
        @library.if_e(4 * i + 8 <= n_bits)
        def _(): # permute the next three columns

            tmp = types.Matrix(num, 4, bs.value_type)
            for ind in range(4):
                tmp.set_column(ind, bs[4 * i + 4 + ind].get_vector())

            sorting.reveal_sort(h, tmp, reverse = True)

            for ind in range(4):
                bs[4 * i + 4 + ind].assign_vector(tmp.get_column(ind))
                           
        # Handle ragged end
        @library.else_
        def ragged():
            @library.if_(n_bits % 4 != 0)
            def mod():
                tmp = types.Matrix(num, n_bits % 4, bs.value_type)
                perm = Array(num, bs.value_type)
                for ind in range(n_bits % 4):
                    tmp.set_column(ind, bs[4 * i + 4 + ind].get_vector())
                sorting.reveal_sort(h, tmp, reverse = True)
                # Now calculate the permutation
                @library.if_e(n_bits % 4 == 1)
                def dest1():
                    perm.assign_vector(dest_comp(
                        tmp.get_column(0)))
                @library_else_
                def not1():
                    @library.if_e(n_bits % 4 == 2)
                    def dest2():
                        perm.assign_vector(double_dest_comp(
                            tmp.get_column(0),
                            tmp.get_column(1)))
                    @library.else_
                    def dest3():
                        perm.assign_vector(triple_dest_comp(
                            tmp.get_column(0),
                            tmp.get_column(1),
                            tmp.get_column(2)))
                        

                sorting.reveal_sort(perm, h, reverse = False)
                
    sorting.reveal_sort(h, D, reverse = True)

    

    
    
