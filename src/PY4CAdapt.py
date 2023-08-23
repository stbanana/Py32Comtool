
# class DataTypeAdapt:
#     def __init__(self):
#         pass

def uint32_to_int32(u32: int) -> int:
    if u32 >= 0x80000000:
        return u32 - 0x100000000
    else:
        return u32