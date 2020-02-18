import os
import re
import configparser
import xml.dom.minidom as xml
import time
from os import path


class StoryProcess:
    def __init__(self, player, story_id):
        self.isReady = False  # 故事载入情况
        self.error_code = 0  # 故事错误码

        self.unfold = False  # 故事开幕情况

        self.player = player  # player身份
        self.flag_list = []  # flag列表
        self.property = {}  # 财产列表
        self.process = 0   # 章节进度
        self.isDelay = 0   # delay设置
        self.capitalization_sensitive = 0  # 大小写敏感设置

        conf = configparser.ConfigParser()
        conf.read(path.join(path.dirname(__file__), 'story_id.ini'), encoding="utf-8-sig")
        # secs = conf.sections()
        # print(secs)
        try:
            self.story_path = conf.get("StoryDatabase", story_id)
            print(self.story_path)

        except Exception:
            print("故事名错误，载入故事失败")
            self.isReady = False
            self.error_code = 201  # error_code:2xx 表示故事载入错误系列，201表示故事名不存在 （1xx表示用户身份验证错误系列）
        else:
            try:
                self.dom = xml.parse(self.story_path)
            except Exception as e:
                print('Error:', e)
                self.isReady = False
                self.error_code = 202  # 故事文件载入错误，请联系管理员
            else:
                # 导入故事完成后从故事导入设定 #
                self.get_setting()
                self.isReady = True  # 指示当前story已经准备完毕

    async def action(self, session):
        message = session.current_arg_text
        if not self.unfold: #第一次响应时,标题开启
            content, method = self.get_interduction()
            print(content)
            print(method)
            await session.send(content)
            await self.charge_method(session, method)
            self.end_chapter() #开启章节
            self.unfold = True
        else:  #匹配用户反应操作
            content, method = self.get_response(message) #匹配response
            if content != None: #匹配成功
                #####插入设置的发送延时#####
                if self.isDelay > 0:
                    time.sleep(self.isDelay)
                await session.send(content) #发送content的内容
                await self.charge_method(session, method) #执行method的内容
                print(content)
            else:
                content, method = self.get_default_response()
                #####插入设置的发送延时#####
                if self.isDelay > 0:
                    time.sleep(self.isDelay)
                await session.send(content)
                await self.charge_method(session, method)  # 执行method的内容



    #########################游戏内置函数对应类内操作###################
    def flag_off(self, flag):
        if flag in self.flag_list:
            self.flag_list.remove(flag)
            print("flag:"+flag+" has been removed")
        else:
            print("flag " + flag + " doesn't exist.")

    def flag_on(self, flag):
        if flag not in self.flag_list:
            self.flag_list.append(flag)
            print("flag:"+flag+" has been appended")
        else:
            print("flag " + flag + " already exist.")

    def property_create(self, property_list): #实际为二参数命令，这里为了方便传参就直接用一个字符串参数丢进去了 命令格式property_create(property,num) 或加方括号的，具体看下面
        if "[" in property_list and "]" in property_list:
            property_list = property_list.split(",")
            for property_pair in property_list:
                property_pair = property_pair[1:-1] #去掉方括号
                pair = property_pair.split(":")
                property = pair[0].strip()
                num = pair[1].strip()
                self.property[property] = int(num)
                print("create "+property+":"+num+" successfully.")
        else:
            pair = property_list.split(",")
            property = pair[0].strip()
            num = pair[1].strip()
            self.property[property] = int(num)
            print("create " + property + ":" + num + " successfully.")

    def property_del(self, property_list): #property_del(property)或property_del(pro1,pro2,pro3)
        if "," in property_list:
            property_list = property_list.split(",")
            for property in property_list:
                property = property.strip()
                if property in self.property:
                    self.property.pop(property)
                    print("delete "+property+" successfully.")
                else:
                    print("property " + property + " doesn't exis.")
        else:
            if property_list in self.property:
                self.property.pop(property_list)
                print("delete " + property_list + " successfully.")
            else:
                print("property " + property_list + " doesn't exis.")

    def property_change(self, change_list): #其实跟create是一模一样的 #现在不一样了，可以一次性更改一坨属性,不能新增属性（防止打错字多出一个属性来） 命令格式 property_change(pro,num)或property_change([pro1:num1],[pro2:num2],[pro3:num3],[pro4:num4]);
        if "[" in change_list and "]" in change_list:
            change_list = change_list.split(",")
            for change_pair in change_list:
                change_pair = change_pair[1:-1] #去掉方括号
                pair = change_pair.split(":")
                property = pair[0].strip()
                num = pair[1].strip()
                if property in self.property:
                    self.property.update({property:int(num)})
                    print("change "+property+":"+num+" successfully.")
                else:
                    print("property "+property+" doesn't exist.")
        else:
            pair = change_list.split(",")
            property = pair[0].strip()
            num = pair[1].strip()
            if property in self.property:
                self.property.update({property: int(num)})
                print("change " + property + ":" + num + " successfully.")
            else:
                print("property " + property + " doesn't exist.")

    def property_add(self, add_list): #应该不会有人批量加属性吧？应该不会吧？property_add(property,num),num为负数就是减
        add_list = add_list.split(",")
        property = add_list[0].strip()
        add_num = add_list[1].strip()
        if property in self.property:
            num = self.property[property]
            num = num + int(add_num)
            self.property.update({property: num})
            print("add " + property + " " + add_num + " successfully, now "+property+" : "+str(num))
        else:
            print("property " + property + " doesn't exist.")


    def end_chapter(self):
        self.process = self.process + 1
        print("chapter enter "+ str(self.process))

    def jump_to_chapter(self, num):
        self.process = int(num)
        print("chapter enter "+ str(self.process))

    async def charge_method(self, session, message):
        class_noarg_method_dic = {"end_chapter":self.end_chapter} #类内不含参数方法
        class_method_dic = {"flag_on": self.flag_on, "flag_off": self.flag_off, "delay":time.sleep, "jump_to_chapter":self.jump_to_chapter,
                            "property_create":self.property_create, "property_del":self.property_del, "property_change":self.property_change, "property_add":self.property_add
                            } #类内含参数方法
        session_method_dic = {"send": session.send}
        if message != "":
            message = message[:-2] #去掉最后一个分号
            methods = message.split(");")
            for method in methods:
                name, arg = method.strip().split("(", 1) #分开函数名与参数
                print(name+" "+arg)
                if name in class_noarg_method_dic: #不含参函数执行
                    act = class_noarg_method_dic[name]
                    act()
                elif name in class_method_dic: #类内函数直接执行
                    try:
                        arg = float(arg)  # 尝试分离数字参数
                    except ValueError:
                        pass
                    act = class_method_dic[name]
                    act(arg)
                elif name in session_method_dic: #需要await的会话函数另外执行
                    #####插入设置的延时#####
                    if self.isDelay > 0:
                        time.sleep(self.isDelay)
                    act = session_method_dic[name]
                    arg = self.format_charge(arg)
                    await act(arg)

    ############################xml匹配获取函数#################################
    def get_response(self, message):
        root = self.dom.documentElement
        story_class = root.getElementsByTagName("class")[1]

        responses = story_class.getElementsByTagName("response")
        for response in responses:
            #########判断chapter是否符合当前process#############
            isChapter = 0
            chapter_number_node = response.getElementsByTagName("chapter_number")[0]
            if chapter_number_node.childNodes == []:  # 如果没有要求chapter  （？还在考虑是否要求必须填写chapter）
                isChapter = 1
            else:
                chapter_numbers = chapter_number_node.childNodes[0].data
                chapter_number_modules = chapter_numbers.split("or")
                for chapter_number in chapter_number_modules:  # 分割为或为单位的flag组
                    if int(chapter_number) == self.process:
                        isChapter = 1
            if isChapter:
                ##########判断关键词是否符合要求#########
                key_node = response.getElementsByTagName("key")[0]
                keys = key_node.childNodes[0].data
                iskey = 0
                key_modules = keys.split(" or ")
                for key_block in key_modules:  # 分割为或为单位的key组
                    key_block = key_block.split(" and ")  # 分割为与为单位的key块
                    iskey_block = 1
                    for key in key_block:
                        key = key.strip()
                        not_key = 0
                        if "not " in key:  # 解析not key 关键字
                            not_key = 1
                        if not self.capitalization_sensitive:
                            key = key.lower()
                            message = message.lower()
                        if re.findall(r"[(](.*)[)]", key):
                            key = re.findall(r"[(](.*)[)]", key)[0]
                            if key not in message and not_key == 0:
                                iskey_block = 0
                            elif key in message and not_key == 1:
                                iskey_block = 0
                        else:
                            if key != message and not_key == 0:
                                iskey_block = 0
                    if iskey_block == 1:
                        iskey += 1
                if iskey:
                    #########判断flag是否符合要求#########
                    flag_node = response.getElementsByTagName("flag")[0]
                    isflag = 0
                    if flag_node.childNodes == []:
                        isflag = 1
                    else:
                        flags = flag_node.childNodes[0].data
                        flag_modules = flags.split("or")
                        for flag_block in flag_modules:  # 分割为或为单位的flag组
                            flag_block = flag_block.split("and")  # 分割为与为单位的flag块
                            isflag_block = 1
                            for flag in flag_block:
                                flag = flag.strip()
                                # print(flag)
                                if flag not in self.flag_list:
                                    isflag_block = 0
                            if isflag_block == 1:
                                isflag += 1
                    if isflag:  # 检查flag是否满足条件存在
                        ########一切条件达成，执行content以及method的返回
                        content_node = response.getElementsByTagName("content")[0]
                        if content_node.childNodes == []:
                            content = ""
                        else:
                            content = content_node.childNodes[0].data
                            content = self.format_charge(content)

                        method_node = response.getElementsByTagName("method")[0]
                        if method_node.childNodes == []:
                            method = ""
                        else:
                            method = method_node.childNodes[0].data

                        return content, method
        return None, None

    def get_interduction(self):
        root = self.dom.documentElement
        story_class = root.getElementsByTagName("class")[0]

        content_node = story_class.getElementsByTagName("content")[0]
        if content_node.childNodes == []:
            content = ""
        else:
            content = content_node.childNodes[0].data
            content = self.format_charge(content)
        method_node = story_class.getElementsByTagName("method")[0]
        if method_node.childNodes == []:
            method = ""
        else:
            method = method_node.childNodes[0].data

        return content, method

    def get_default_response(self):
        root = self.dom.documentElement
        story_class = root.getElementsByTagName("class")[2] #获取默认回复设置

        responses = story_class.getElementsByTagName("response")
        for response in responses:
            isChapter = 0
            chapter_number_node = response.getElementsByTagName("chapter_number")[0]
            if chapter_number_node.childNodes == []:  # 如果没有要求chapter  （？还在考虑是否要求必须填写chapter）
                isChapter = 1
            else:
                chapter_numbers = chapter_number_node.childNodes[0].data
                chapter_number_modules = chapter_numbers.split("or")
                for chapter_number in chapter_number_modules:  # 分割为或为单位的flag组
                    if int(chapter_number) == self.process:
                        isChapter = 1
            if isChapter:
                flag_node = response.getElementsByTagName("flag")[0]
                isflag = 0
                if flag_node.childNodes == []:
                    isflag = 1
                else:
                    flags = flag_node.childNodes[0].data
                    flag_modules = flags.split("or")
                    for flag_block in flag_modules:  # 分割为或为单位的flag组
                        flag_block = flag_block.split("and")  # 分割为与为单位的flag块
                        isflag_block = 1
                        for flag in flag_block:
                            flag = flag.strip()
                            # print(flag)
                            if flag not in self.flag_list:
                                isflag_block = 0
                        if isflag_block == 1:
                            isflag += 1
                if isflag:  # 检查flag是否满足条件存在
                    content_node = response.getElementsByTagName("content")[0]
                    if content_node.childNodes == []:
                        content = ""
                    else:
                        content = content_node.childNodes[0].data
                        content = self.format_charge(content)

                    method_node = response.getElementsByTagName("method")[0]
                    if method_node.childNodes == []:
                        method = ""
                    else:
                        method = method_node.childNodes[0].data

                    return content, method
        return "", ""

    def get_setting(self):
        root = self.dom.documentElement
        setting_class = root.getElementsByTagName("class")[3]  # 获取setting
        self.isDelay = float(setting_class.getElementsByTagName("isDelay")[0].childNodes[0].data)  # isDelay的setting
        self.capitalization_sensitive = float(setting_class.getElementsByTagName("capitalization_sensitive")[0].childNodes[0].data)




    def format_charge(self, content):
        return_content = ""
        contents = content.split("%%")  # 将原先的%号位置记录下来
        for i in contents:  # 每个i后都需要跟一个原先的%
            variables = re.findall(r"%(.+?)\s", i, re.S)
            units = re.split(r"%.+?\s", i, re.S)
            print(units)
            k = ""
            for num in range(len(variables)):
                if variables[num] in self.property:
                    variable = str(self.property[variables[num]])
                else:
                    print("error: no such property name:" + variables[num])
                    variable = ""
                k += units[num] + variable
            k += units[len(variables)]
            return_content += k + "%"

        return return_content[:-1]


