from nonebot import on_command, CommandSession, permission
from nonebot import on_natural_language, NLPSession, IntentCommand
import nonebot
from .data_source import StoryProcess
import re
import time
import os

@on_command('活动', permission= permission.PRIVATE)
async def activity(session: CommandSession):
    await session.send("") #活动结束操作

# activity.args_parser 装饰器将函数声明为 活动命令的参数解析器
# 此处的命令解析器用于持续不断循环活动
@activity.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        Story = StoryProcess("admin", "测试故事") # 第一个参数为玩家身份，第二个参数为剧本名称
        session.state['Story'] = Story
    if session.current_arg_text != '退出':
        Story = session.state['Story']
        await Story.action(session)
        session.state['Story'] = Story
        session.pause()
    else:  #退出后要做的动作
        bot = session.bot
        await bot.send_group_msg(group_id=1020570636, message="测试样例")
    return

