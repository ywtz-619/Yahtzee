import traceback

from pkg.plugin.context import (
    APIHost,
    BasePlugin,
    EventContext,
    handler,
    llm_func,
    register,
)
from pkg.plugin.events import *  # 导入事件类

from .yahtzee import COMMAND_PREFIX, Command, CommandHandler, GameSessionManager


# 注册插件
@register(name="Yahtzee", description="随时随地在群聊中来一局好玩的快艇骰子！", version="0.1", author="Yuwen")
class Yahtzee(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.session_manager = GameSessionManager()
        self.command_prefix = self.config["command_prefix"]

    # 异步初始化
    async def initialize(self):
        pass
    
    def _handle_message(self, ctx: EventContext, is_private: bool):
        msg = ctx.event.text_message
        if not msg.startswith(COMMAND_PREFIX):
            return
        # 当前sender（用户/群）没有开启游戏会话时，排除初始指令以外的指令
        if ctx.event.launcher_id not in self.session_manager.sessions:
            # 私聊模式下，只响应START指令（直接开启游戏）
            if is_private and msg != Command.START:
                return
            # 群聊模式下，只响应JOIN指令（创建或加入游戏房间）
            if not is_private and msg != Command.JOIN:
                return
        self.ap.logger.info(f"Yahtzee: 收到消息, launcher_id={ctx.event.launcher_id}, sender_id={ctx.event.sender_id}, msg={msg}")
        try:
            command_handler = CommandHandler(self.session_manager, is_private=is_private)
            msg = command_handler.handle_command(ctx.event.launcher_id, ctx.event.sender_id, msg)
            # 目前暂时只需要靠返回文本内容判断结束游戏，销毁会话，不稳定但够用了
            if "游戏结束！" in msg:
                self.session_manager.remove_session(ctx.event.launcher_id)
                self.ap.logger.info(f"Yahtzee: 游戏结束, 会话：{ctx.event.launcher_id}")
        except Exception as e:
            self.ap.logger.error(f"Yahtzee: 处理命令时发生错误: {traceback.format_exc()}")
            msg = f"发生错误"
        finally:
            # 检查当前机器人群聊中回复是否@发送者，添加换行
            if not is_private and self.ap.platform_cfg.data['at-sender']:
                msg = f"\n{msg}"
            ctx.add_return("reply", [msg])
            ctx.prevent_default()

    # 当收到个人消息时触发
    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        self._handle_message(ctx, is_private=True)

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        self._handle_message(ctx, is_private=False)

    # 插件卸载时触发
    def __del__(self):
        pass
