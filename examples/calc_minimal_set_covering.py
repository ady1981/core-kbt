from kbt_core.minimal_set_covering import calc_set_covering


def main():
    result = calc_set_covering(3, [[1], [1, 2], [2, 3]])
    print(result)


main()