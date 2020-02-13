from datetime import datetime
from xlrd import xldate_as_tuple
import xlrd

workbook = "C:\\Users\\Jade\\Desktop\\龙胶危机统计信息.xlsx"

async def search_qq(qqnum: float):
    data = xlrd.open_workbook(workbook)  # 打开表格路径
    table = data.sheets()[0]  # 取第几张表 0为序号表
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    for i in range(2, nrows):  # 按行遍历，从第3行开始

        info = table.cell(i, 3).value  # 让info等于每一行第四列的值（即qq号）
        message = ""  # 初始化message变量，使其为空字符串

        if qqnum == info:  # 如果与传进来的qq号码数据相同
            output_list = [1, 3, 0, 11, 12, 5, 6, 7, 8, 9, 10]  # 表格内的数字代表第几列的内容，增加或减少数字可以增删输出内容，调换数字顺序可以调换输出排列顺序

            for j in output_list:
                element_name = table.cell(1, j).value  # 需要输出的内容的标题
                element_name = element_name.replace("\n", "")  # 删除原本标题中的换行

                element = table.cell(i, j).value  # 需要输出的内容

                ctype = table.cell(i, j).ctype  # 数值类型，主要是为了改日期，日期的ctype值为3，字符串为1

                if ctype == 3:  # 如果是日期信息
                    if element == 0:
                        element = "非通行证用户或通行证已到期"
                    else:
                        date = datetime(*xldate_as_tuple(element, 0))  # 转换格式为标准时间格式
                        element = date.strftime('%Y-%m-%d')  # 输出格式为年/月/日，可改动

                if j in [0, 3, 5, 6, 7, 8, 9, 10]:  # 这样就不用把表格里的qq号改成字符串类了，这里会自动把小数点去掉 可以在条件里追加要去掉小数点的列
                    element = int(element)

                message = message + element_name + ":" + str(element) + "\n"  # 为message追加内容
            return message.strip()
    return False  # 如果到最后都没有匹配到，就返回Fasle