from nonebot import on_command, CommandSession, permission
from nonebot import on_natural_language, NLPSession, IntentCommand
import nonebot
from .data_source import StoryProcess
import re
import time
import os


@on_command('活动', permission=permission.PRIVATE)
async def activity(session: CommandSession):
    if session.current_arg_text == '退出':  # 退出后要做的动作
        bot = session.bot
        await bot.send_group_msg(group_id=1020570636, message="测试样例")
    elif not session.state['isLoad']:  # 如果还未载入故事
        story_name = session.get('story_name', prompt='请输入要进入的故事')  # 尝试向用户获取故事名，若没有获取到，则发送prompt中的消息
        Story = StoryProcess("admin", story_name)  # 第一个参数为玩家身份，第二个参数为剧本名称
        if Story.isReady:
            session.state['Story'] = Story
            session.state['isLoad'] = True  # 表明已经载入故事
            print("故事载入成功")
        else:
            if Story.error_code == 201:  #错误码201表示故事名错误（2xx为故事载入错误，1xx预留给玩家验证错误
                session.pause("故事名不存在，请重新输入")

    if session.current_arg_text != '退出' and session.state['isLoad']:
        Story = session.state['Story']
        await Story.action(session)
        session.state['Story'] = Story
        session.pause()
    await session.send("")  # 活动结束操作

# activity.args_parser 装饰器将函数声明为 活动命令的参数解析器
# 此处的命令解析器用于解析故事名
@activity.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白字符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:  # 第一次开启会话，判断是不是自带故事参数
        session.state['isLoad'] = False  # 插个旗子，isLoad判断是不是已经输入过故事名
        if stripped_arg:
            session.state['story_name'] = stripped_arg
        return

    if not session.state['isLoad'] and not stripped_arg:  # 如果输入空白字符
        session.pause("故事名不能为空呢,请选择故事")
    return


