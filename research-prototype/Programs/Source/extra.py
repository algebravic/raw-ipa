"""
Extra debugging routines.
"""
def print_property(fun, vec, msg):

    print_ln("%s: %s", msg, tree_reduce(operator.add,fun(vec)).reveal())

def reconstruct(bit_array: Matrix) -> Array:
    """
    bit_array is an N by B array of bits
    compute the integer representation.
    This should only involve scalar multiplies and adds.
    """

    num, n_bits = bit_array.sizes
    result = Array(num, sint)
    result.assign_vector(bit_array.get_column(n_bits - 1))
    for ind in range(n_bits - 2, -1, -1):
        result = result + result + bit_array.get_column(ind)
    return result

def validate_bits(arr: Array) -> Tuple[sint, sint]:
    """
    Test a purported bit vector.
    """

    small = arr.get_vector() < 0
    big = arr.get_vector() > 1

    return (tree_reduce(operator.add, small),
            tree_reduce(operator.add, big))

