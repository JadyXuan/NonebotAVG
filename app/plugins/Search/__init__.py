from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from .data_source import search_qq
import re
import time
import os


memory_of_qqnum = ""
memory_of_state = 0
reply_sentences = ["该用户不在我们的名单里","说了不在我们名单里，你丫有完没完", "不想帮你查了，你爬吧", "[CQ:emoji,id=128116]不想[CQ:emoji,id=128036]你个铁[CQ:emoji,id=127828][CQ:emoji,id=127828]","爪巴"]





# on_command 装饰器将函数声明为一个命令处理器
# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」

@on_command('查询')
async def search(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    qqnum = session.get('qqnum')
    global memory_of_qqnum
    global memory_of_state
    global reply_sentences
    if qqnum:
        print("search for" + qqnum)
        state_report = await search_qq(float(qqnum))
        if state_report:
            # 向用户发送天气预报
            await session.send(state_report)
            memory_of_state = 0
            memory_of_qqnum = qqnum
        elif memory_of_qqnum != qqnum:
            memory_of_qqnum = qqnum
            memory_of_state = 1
            await session.send("检测到该用户不在我们的名单中嗷")
        elif memory_of_state >= 1 and memory_of_state < 6:
            await session.send(reply_sentences[memory_of_state-1])
            memory_of_state += 1
        elif session.ctx['message_type']=="group":
            bot = session.bot
            await bot.set_group_ban(group_id=session.ctx['group_id'], user_id=3159495381, duration=50)
            await bot.send_private_msg(user_id=session.ctx['user_id'],message='[CQ:shake,id=1]')
            memory_of_state = 0


# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@search.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['qqnum'] = stripped_arg
        if not stripped_arg:
            session.state['qqnum'] = str(session.ctx['user_id'])
        return



@on_command('test', aliases=('测试','测验'))
async def test(session: CommandSession):
    while True:
        #await session.send("[CQ:dice,type=3]")
        await session.send(session.current_arg_text)
        #await session.send("[CQ:record,file=file://C:\\Users\\Jade\\Desktop\\test.mp3]")



#自然语言处理
@on_natural_language(keywords={'查询'})
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    arg = ""
    if re.search('[0-9]{5,10}', stripped_msg):
        p = re.compile('[0-9]{5,10}')
        arg = p.findall(stripped_msg)[0]
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, '查询', current_arg=arg)


