# 一个存储解析.hex文件数据的类  -->
# class HexInstruct(Enum):
#     Data_Rrecord = 0x00  # 标识记录数据 单行数据段是存储的数据
#     End_File_Record = 0x01  # 标识文件结束 每个.hex结尾都是:00000001FF
#     Extended_Segment_Address = 0x02  # 标识拓展段地址记录 x86寻址 单行数据段包含一个16位段基址 该基址乘以16，后续每个记录数据行的地址，都需要加上这个值
#     Start_Segment_Address = 0x03  # 标识开始段地址记录 x86寻址 允许32位寻址，CS：IP寄存器的起始地址，前两个数据字节是CS值，后两个是IP值
#     Extended_Linear_Address = 0x04  # 标识扩展线性地址的记录 数据段记录扩展线性地址 后续每个0x02记录数据行，的地址，都以此记录作为高16位
#     Start_Linear_Address = 0x05  # 标识开始线性地址记录 数据段是线性起始地址
#
#
# class PY_HEX_Analysis:
#     def __init__(self):
#         self.data = ""
#         self.datalen = ""
#         self.datatype = ""
#   <--
