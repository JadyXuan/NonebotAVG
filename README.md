# NonebotAVG
这是一个测试项目，尝试开发一个小型的聊天用AVG文字冒险游戏制作器，以qq作为平台，依赖nonebot框架互动特性制作文字冒险类游戏。
目前由于nonebot难以支持大型化的文字活动，故将文字冒险游戏剧本制作为xml形式存储，依靠插件读取的方式导入剧本。

app/plugins/Story文件夹下的data_source.py文件为剧本导入与事件处理插件
__init__.py是普通的Nonebot插件文件。data_source定义了Story类作为游戏进度类，在init当中初始化Story类后使用Story.action(msg)来传入用户会话。
目前仅支持nonebot框架（因为用过的qq机器人框架就两个xwx）


会尽早把剧本编辑器肝出来