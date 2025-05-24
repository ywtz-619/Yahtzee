import random
from collections import Counter
from enum import Enum, StrEnum

COMMAND_PREFIX = ""

NUM_INDEX = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}

NUM_DICE = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣"}

RANKS = {
    1: "🥇",
    2: "🥈",
    3: "🥉",
    4: "4️⃣",
    5: "5️⃣",
}

class Command(StrEnum):
    JOIN = "加入快艇"
    QUIT = "退出快艇"
    START = "开始快艇"
    ROLL = "掷"
    HOLD = "定"
    HOLDROLL = f"{HOLD}{ROLL}"
    SCORE = "记"
    DICE = "骰"
    STOP = "结束快艇"

class CommandHint(StrEnum):
    JOIN = f"【{COMMAND_PREFIX}{Command.JOIN} <可选昵称>】加入房间"
    QUIT = f"【{COMMAND_PREFIX}{Command.QUIT}】退出房间"
    START = f"【{COMMAND_PREFIX}{Command.START}】开始游戏（房主）"
    ROLL = f"【{COMMAND_PREFIX}{Command.ROLL}】掷骰子"
    HOLD = f"【{COMMAND_PREFIX}{Command.HOLD} 135】固定对应序号骰子"
    HOLD_0 = f"【{COMMAND_PREFIX}{Command.HOLD} 0】取消固定骰子"
    HOLDROLL = f"【{COMMAND_PREFIX}{Command.HOLDROLL} 135】固定骰子并投掷"
    HOLDROLL_0 = f"【{COMMAND_PREFIX}{Command.HOLDROLL} 0】取消固定并投掷"
    VIEW_SCORE = f"【{COMMAND_PREFIX}{Command.SCORE}】查看记分板"
    SCORE = f"【{COMMAND_PREFIX}{Command.SCORE} 快艇】直接记分"
    DICE = f"【{COMMAND_PREFIX}{Command.DICE}】查看骰子"
    STOP = f"\n【{COMMAND_PREFIX}{Command.STOP}】强制结束游戏"

class Emoji(StrEnum):
    DICE = "🎲"
    BOAT = "🚤"
    RED = "🟥"
    GREEN = "🟩"
    BLUE = "🟦"
    CLEAR = "🔲"
    CHECK = "☑️"

class Die:
    def __init__(self):
        self._value = random.randint(1, 6)
        self._held = False

    def roll(self):
        self._value = random.randint(1, 6)

    @property
    def value(self):
        return self._value

    @property
    def held(self):
        return self._held

    @held.setter
    def held(self, is_held: bool):
        self._held = is_held


class Dice:
    def __init__(self):
        self._dice = self._init_dice()

    def _init_dice(self):
        return [Die() for _ in range(5)]

    def roll(self):
        for die in self._dice:
            if not die.held:
                die.roll()

    def hold(self, indices: list[int]):
        """固定指定索引的骰子（直接更新全部骰子状态，以指定为准）"""
        for index, die in enumerate(self._dice):
            die.held = index in indices

    def reset(self):
        self._dice = self._init_dice()

    @property
    def dice(self):
        return self._dice


class ScoreBoard:
    def __init__(self):
        self._total_score = 0
        self._scores = self._init_scores()

    def _init_scores(self):
        scores = {
            # 上区
            "一点": {"score": 0, "add": 0, "selected": False},
            "两点": {"score": 0, "add": 0, "selected": False},
            "三点": {"score": 0, "add": 0, "selected": False},
            "四点": {"score": 0, "add": 0, "selected": False},
            "五点": {"score": 0, "add": 0, "selected": False},
            "六点": {"score": 0, "add": 0, "selected": False},
            "累计": {"score": 0},
            "加成": {"score": 0},
            # 下区
            "全选": {"score": 0, "add": 0, "selected": False},
            "三条": {"score": 0, "add": 0, "selected": False},
            "四条": {"score": 0, "add": 0, "selected": False},
            "葫芦": {"score": 0, "add": 0, "selected": False},
            "小顺": {"score": 0, "add": 0, "selected": False},
            "大顺": {"score": 0, "add": 0, "selected": False},
            "快艇": {"score": 0, "add": 0, "selected": False},
            # 总分
            "总分": {"score": self._total_score},
        }
        return scores

    def _get_upper_total_score(self):
        sum = 0
        for key in ["一点", "两点", "三点", "四点", "五点", "六点"]:
            sum += self._scores[key]["score"]
        return sum

    def _clear_add(self):
        for key, data in self._scores.items():
            if data.get("add", None):
                self._scores[key]["add"] = 0


    def cal_scores(self, dice: Dice):
        values = [die.value for die in dice.dice]
        counts = Counter(values)
        self._scores["一点"]["add"] = counts[1] * 1
        self._scores["两点"]["add"] = counts[2] * 2
        self._scores["三点"]["add"] = counts[3] * 3
        self._scores["四点"]["add"] = counts[4] * 4
        self._scores["五点"]["add"] = counts[5] * 5
        self._scores["六点"]["add"] = counts[6] * 6
        self._scores["全选"]["add"] = sum(values)
        self._scores["三条"]["add"] = sum(values) if max(counts.values()) >= 3 else 0
        self._scores["四条"]["add"] = sum(values) if max(counts.values()) >= 4 else 0
        self._scores["葫芦"]["add"] = 25 if sorted(counts.values()) == [2, 3] else 0
        self._scores["小顺"]["add"] = (
            30
            if any(
                set(seq).issubset(set(values))
                for seq in ([1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6])
            )
            else 0
        )
        self._scores["大顺"]["add"] = (
            40 if set(values) in (set([1, 2, 3, 4, 5]), set([2, 3, 4, 5, 6])) else 0
        )
        self._scores["快艇"]["add"] = 50 if max(counts.values()) == 5 else 0

    def set_scores(self, item: str, score: int):
        self._scores[item]["score"] = score
        self._scores[item]["selected"] = True
        self._total_score += score
        self._scores["总分"]["score"] = self._total_score
        if item in ["一点", "两点", "三点", "四点", "五点", "六点"]:
            upper_total_score = self._get_upper_total_score()
            self._scores["累计"]["score"] = upper_total_score
            if upper_total_score >= 63:
                self._scores["加成"]["score"] = 35
                self._total_score += 35
        self._clear_add()

    @property
    def scores(self):
        return self._scores

    @property
    def total_score(self):
        return self._total_score

    def reset(self):
        self._scores = self._init_scores()


class TurnState(Enum):
    WAITING = 0  # 等待玩家首次投掷
    ROLLING = 1  # 玩家投掷机会未用完
    ROLLED = 2  # 玩家投掷机会已用完


class Player:
    def __init__(self, _id: str, name: str):
        self.id = _id
        self.name = name
        self.dice = Dice()
        self.score_board = ScoreBoard()
        self.rolls_left = 3
        self.state = TurnState.WAITING

    def roll(self):
        self.dice.roll()
        self.rolls_left -= 1

    def hold(self, indices: list[int]):
        self.dice.hold(indices)

    def init_turn(self):
        self.dice.reset()
        self.rolls_left = 3
        self.state = TurnState.WAITING

    def reset(self):
        self.init_turn()
        self.score_board.reset()


class GameState(Enum):
    LOBBY = 1  # 已有玩家触发游戏会话，等待其他玩家加入或游戏开始
    PLAYING = 2  # 游戏进行中
    GAME_OVER = 3  # 所有玩家都完成游戏，或游戏中断


class GameSession:
    def __init__(self, host_player_id: str, group_id: str, host_player_name:str=None, is_private: bool = False):
        self.id = group_id  # 对局ID，直接用群ID
        self.is_private = is_private
        if host_player_name is None:
            host_player_name = host_player_id
        self.players = [Player(host_player_id, host_player_name)]  # 玩家列表
        self.host_player = self.players[0]  # 房主
        self.state = GameState.LOBBY
        self.current_player_index = 0  # 当前玩家索引
        self.current_player = self.players[self.current_player_index]  # 当前玩家
        self.round = 1  # 当前回合数
        self.messenger = Messenger(self)

    def _finish_turn(self):
        last_player_score = self.messenger.msg_scoring(is_turn_over=True)
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            self.round += 1
            if self.round > 13:
                self.state = GameState.GAME_OVER
                return self.game_over()
            for player in self.players:
                player.init_turn()
        self.current_player = self.players[self.current_player_index]
        self.state = GameState.PLAYING
        return last_player_score + "\n\n" + self.messenger.msg_waiting()

    def add_player(self, player_id: str, player_name: str=None):
        if player_name is None:
            player_name = player_id
        session_player_ids = [player.id for player in self.players]
        session_player_names = [player.name for player in self.players]
        if player_id in session_player_ids:
            return f"你已在房间内" + "\n" + self.messenger.msg_lobby()
        if len(self.players) >= 5:
            return f"房间已满5人，无法加入" + "\n" + self.messenger.msg_lobby()
        if player_id in session_player_names:
            return f"有人抢先使用了你的ID做昵称，请用【{COMMAND_PREFIX}{Command.JOIN}】 xxx另取个昵称"
        if player_name in session_player_names:
            return f"昵称已被占用"
        if player_name in session_player_ids:
            return f"不能用当前玩家ID做昵称"

        self.players.append(Player(player_id, player_name))
        return self.messenger.msg_lobby()

    def remove_player(self, player_id: str):
        for player in self.players:
            if player.id == player_id:
                self.players.remove(player)
                return self.messenger.msg_lobby()
        return "你不在房间内"

    def start_game(self):
        self.state = GameState.PLAYING
        return (
            f"{Emoji.DICE}游戏开始{Emoji.DICE}"
            + "\n"
            + self.messenger.msg_waiting()
        )

    def roll(self):
        player = self.current_player
        if all(die.held for die in player.dice.dice):
            return "所有骰子都已固定"
        player.roll()
        player.state = TurnState.ROLLING
        if player.rolls_left == 0:
            player.state = TurnState.ROLLED
        # 若你已在Yahtzee的地方计分, 每再额外掷出一个Yahtzee则会得到 100 额外的奖分
        # 印象中有的版本没有这个设定，还是加上
        counts = Counter([die.value for die in player.dice.dice])
        if max(counts.values()) == 5 and player.score_board.scores["快艇"]["selected"]:
            player.score_board.scores["快艇"]["score"] += 100
            player.score_board.scores["总分"]["score"] += 100
            return self.messenger.msg_dice(if_yahtzee_bonus=True)
        return self.messenger.msg_dice()

    def hold(self, indices: list[int]):
        self.current_player.hold(indices)
        return self.messenger.msg_dice()
    
    def unhold(self):
        self.current_player.hold([])
        return self.messenger.msg_dice()

    def dice(self):
        return self.messenger.msg_dice()

    def score(self, item: str):
        player = self.current_player
        score_item = player.score_board.scores.get(item, {})
        if score_item.get("selected", False) and score_item["selected"]:
            return "不能重复记分"
        player.score_board.cal_scores(player.dice)
        add = score_item.get("add", None)
        if add is None:
            return "记分类别错误"
        player.score_board.set_scores(item, add)
        return self._finish_turn()

    def view_score(self):
        return self.messenger.msg_scoring()

    def get_result(self):
        sorted_players = sorted(
            self.players, key=lambda player: player.score_board.total_score, reverse=True
        )
        highest_score = sorted_players[0].score_board.total_score
        winners = []
        ranks = []

        if highest_score == 0:
            return "游戏结束！没有人得分"
        
        current_rank = 1
        previous_score = None
        for i, player in enumerate(sorted_players):
            score = player.score_board.total_score
            if score != previous_score:
                current_rank = i + 1
            ranks.append(f"{RANKS[current_rank]} {player.name}：{player.score_board.total_score}")
            if score == highest_score:
                winners.append(player.name)
            previous_score = score
        if len(winners) == 1:
            winners_text = f"第一名：{winners[0]}"
        else:
            winners_text = f"并列第一名：{'、'.join(winners)}"
        ranks_text = "\n".join(ranks)
        return "游戏结束！\n" + winners_text + "\n\n" + ranks_text

    def game_over(self):
        if self.is_private:
            return self.messenger.msg_scoring(is_turn_over=True) + "\n" + "游戏结束！"
        else:
            return self.get_result()
        


class Messenger:

    def __init__(self, session: GameSession):
        self.session = session

    @property
    def turn_header(self):
        """固定消息头，用于标记当前是谁的回合"""
        if self.session.is_private:
            return ""
        return (
            f"{Emoji.DICE}玩家{self.session.current_player.name}{Emoji.DICE}"
        )

    def msg_lobby(self):
        """列出当前房间内玩家"""
        title = f"{Emoji.DICE}快艇骰子游戏房间{Emoji.BOAT}"
        player_names = []
        for i, player in enumerate(self.session.players):
            name = f"{player.name}（房主）" if i == 0 else player.name
            player_names.append(f"{NUM_INDEX[i+1]} - {name}")
        replys = [
            f"{title}\n\n当前玩家：\n{'\n'.join(player_names)}\n",
            CommandHint.JOIN,
            CommandHint.QUIT,
            CommandHint.START,
        ]        
        # if self.session.current_player == self.session.host_player:
        #     replys.append(CommandHint.STOP)
        return "\n".join(replys)

    def msg_waiting(self):
        """回合开始时等待玩家指令"""
        if self.session.is_private:
            name = "你"
        else:
            name = f"【{self.session.current_player.name}】"
        replys = [f"等待{name}行动...\n{CommandHint.ROLL}"]
        if self.session.current_player == self.session.host_player:
            replys.append(CommandHint.STOP)
        return "\n".join(replys)

    def msg_dice(self, if_yahtzee_bonus=False):
        """显示当前玩家骰子状态"""
        player = self.session.current_player
        commands = []
        if player.state == TurnState.ROLLING:
            commands.extend(
                [
                    f"{CommandHint.ROLL}（剩余{player.rolls_left}次）",
                    CommandHint.HOLD,
                    CommandHint.HOLD_0,
                    CommandHint.HOLDROLL,
                    CommandHint.HOLDROLL_0,
                ]
            )
        commands.extend(
            [
                CommandHint.VIEW_SCORE,
                CommandHint.SCORE,
            ]
        )
        if player == self.session.host_player:
            commands.append(CommandHint.STOP)
        dice_result = []
        dice = player.dice
        for i, die in enumerate(dice.dice):
            is_held = Emoji.RED if die.held else Emoji.GREEN
            dice_result.append(f"{NUM_INDEX[i+1]}　{is_held}{NUM_DICE[die.value]}")
        replys = [
            self.turn_header,
            "\n".join(dice_result),
            "\n",
            "\n".join(commands),
        ]
        if if_yahtzee_bonus:
            replys.insert(2, "再次掷出快艇🚤，额外奖励100分！")
        return "\n".join(replys)

    def msg_scoring(self, is_turn_over: bool = False):
        """显示当前玩家记分板"""
        player = self.session.current_player
        if not is_turn_over:
            commands = [
                CommandHint.SCORE,
                CommandHint.DICE,
            ]
            if player == self.session.host_player:
                commands.append(CommandHint.STOP)
            commands = "\n".join(commands)
        else:
            commands = ""
        board = player.score_board
        board.cal_scores(player.dice)  # 先算当前分型
        upper = []
        lower = []
        for score_item, data in board.scores.items():
            score = data.get("score")
            add = data.get("add", None)
            selected = data.get("selected", None)
            if add is not None:
                add = f"　(+{add})" if not is_turn_over else ""
                selected = Emoji.CHECK if selected else Emoji.CLEAR
                item = f"{selected}　{score_item}　{score}{add}"
            else:
                item = f"　　 {score_item}　{score}"
            if score_item in [
                "一点",
                "两点",
                "三点",
                "四点",
                "五点",
                "六点",
                "累计",
                "加成",
            ]:
                upper.append(item)
            else:
                lower.append(item)
        upper = "\n".join(upper)
        lower = "\n".join(lower)
        splitter = "=" * 14 
        replys = [
            self.turn_header,
            splitter,
            upper,
            splitter,
            lower,
            splitter,
            commands,
        ]
        return "\n".join(replys)


class GameSessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, host_player_id: str, group_id: str,host_player_name:str=None, is_private: bool = False):
        if host_player_name is None:
            host_player_name = host_player_id
        session = GameSession(host_player_id, group_id, host_player_name=host_player_name, is_private=is_private)
        self.sessions[group_id] = session
        return session.messenger.msg_lobby()

    def remove_session(self, session_id: str):
        if session_id in self.sessions.keys():
            del self.sessions[session_id]


class CommandHandler:
    def __init__(self, session_manager: GameSessionManager, is_private: bool = False):
        self.is_private = is_private
        self.manager = session_manager

    def _parse_command(self, command_str:str):
        parts = command_str.strip().split(maxsplit=1)
        if not parts:
            return None, None
        command = parts[0]
        arg = parts[1] if len(parts) > 1 else None
        return command, arg

    def handle_command(self, launcher_id: str, sender_id: str, command_str: str) -> str:
        """command这里不带指令前缀"""
        session = self.manager.sessions.get(launcher_id, None)
        command, arg = self._parse_command(command_str)

        # 私聊模式中，直接指令开始游戏
        if self.is_private:
            if not session:
                # 考虑是纯文本交互环境，指令验证还是严格一点好
                # 例如开始游戏是/start，则输入/start 123不应该通过
                if command == Command.START and not arg:
                    self.manager.create_session(sender_id, launcher_id, is_private=True)
                    session = self.manager.sessions[launcher_id]
                    session.add_player(sender_id)
                    return session.start_game()
                else:
                    return f"游戏还未开始，发送【{COMMAND_PREFIX}{Command.START}】开始游戏"

        # 群聊中有游戏房间环节
        else:
            # 游戏房间未创建
            if not session:
                if command == Command.JOIN:
                    # 群里当前没有会话，当前玩家成为房主
                    msg = self.manager.create_session(sender_id, launcher_id, host_player_name=arg, is_private=self.is_private)
                    self.manager.sessions[launcher_id].state = GameState.LOBBY
                    return msg
                else:
                    return f"当前没有游戏房间，首位发送【{COMMAND_PREFIX}{Command.JOIN} <可选昵称>】的玩家创建房间"

            # 游戏房间已创建，等待玩家加入并开始
            if session.state == GameState.LOBBY:
                if command == Command.JOIN:
                    return session.add_player(sender_id, player_name=arg)
                elif command == Command.QUIT and not arg:
                    if sender_id == session.host_player.id:
                        self.manager.remove_session(launcher_id)
                        return "房主已退出，房间解散"
                    else:
                        return session.remove_player(sender_id)
                elif command == Command.START and not arg:
                    if sender_id != session.host_player.id:
                        return "只有房主可以开始游戏"
                    return session.start_game()
                else:
                    replys = [
                        f"指令有误\n",
                        CommandHint.JOIN,
                        CommandHint.QUIT,
                        CommandHint.START,
                    ]
                    return "\n".join(replys)

        # 游戏开始
        if session.state == GameState.PLAYING:
            if sender_id != session.current_player.id:
                return f"请等待{session.current_player.name}行动"

            if command == Command.ROLL and not arg:
                if session.current_player.state == TurnState.ROLLED:
                    return "投掷机会已用完，请记分"
                return session.roll()

            elif command == Command.HOLD and arg:
                if session.current_player.state == TurnState.WAITING:
                    return "还未掷骰子"
                if session.current_player.state == TurnState.ROLLED:
                    return "投掷机会已用完，请记分"
                if arg == "0":
                    return session.unhold()
                try:
                    indices = [int(num) - 1 for num in arg]
                    return session.hold(indices)
                except Exception:
                    return f"指令有误\n\n{CommandHint.HOLD}"
                  
            elif command == Command.HOLDROLL and arg:
                if session.current_player.state == TurnState.WAITING:
                    return "还未掷骰子"
                if session.current_player.state == TurnState.ROLLED:
                    return "投掷机会已用完，请记分"
                if arg == "0":
                    session.unhold()
                    return session.roll()
                try:
                    indices = [int(num) - 1 for num in arg]
                    session.hold(indices)
                    return session.roll()
                except Exception:
                    return f"指令有误\n\n{CommandHint.HOLD}"

            elif command == Command.SCORE:
                if not arg:
                    return session.view_score()
                if session.current_player.state == TurnState.WAITING:
                    return "还未掷骰子"
                return session.score(arg)

            elif command == Command.DICE and not arg:
                if session.current_player.state == TurnState.WAITING:
                    return "还未掷骰子"
                return session.dice()

            elif command == Command.STOP and not arg:
                if sender_id != session.host_player.id:
                    return "只有房主可以强制结束游戏"
                session.state = GameState.GAME_OVER
                self.manager.remove_session(launcher_id)
                return session.game_over()

            else:
                replys = [
                    "指令有误\n",
                    CommandHint.ROLL,
                    CommandHint.HOLD,
                    CommandHint.HOLD_0,
                    CommandHint.HOLDROLL,
                    CommandHint.HOLDROLL_0,
                    CommandHint.VIEW_SCORE,
                    CommandHint.SCORE,
                    CommandHint.DICE,
                ]
                if session.current_player == session.host_player:
                    replys.append(CommandHint.STOP)
                return "\n".join(replys)
