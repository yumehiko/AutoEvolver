from .ui_base import UIBase
from .role import Role
from .chat_message import ChatMessage
from .talker import Talker
from .bot_agent import BotAgent
from .file_reader import FileReader
from .message_carrier import MessageCarrier
from .task import Task, TaskTag
from dotenv import load_dotenv
import asyncio
import openai
import os

class Session():
    """
    自律型タスク解決セッション。
    """

    def __init__(self, view: UIBase) -> None:
        self.view = view
        self.message_carrier = MessageCarrier(view)
        self.file_reader = FileReader()
        # APIキーを.envから読み込む。
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        # OpenAIのAPIキーが設定できたか確認し、設定されていない場合は例外を返す
        if not openai.api_key:
            raise ValueError("APIKey is not set.")
        
    async def run(self) -> None:
        # 1. objectiveとそのcontextを受ける
        # 2. objectiveをtasksに分割する
        # 3. tasksを解決可能なresolvablesとunresolvablesに分割する
        # 4. unresolvablesをもとに、追加すべき機能をまとめ、need_function_tasksとする
        # 5. need_function_tasksをresolvablesとunresolvablesに分割し、それぞれに分配する。
        # 6. 4-5を繰り返し、unresolvablesが空になるまで繰り返す
        # 7. resolvablesを解決する
        self.message_carrier.print_message_as_system("\n=== Start Session ===", True)
        agent = BotAgent()  
        objective, context = await self.determine_objective(agent)
        tasks = self.split_to_tasks(agent, objective, context)
        await self.end()

    async def end(self) -> None:
        self.message_carrier.print_message_as_system("\n=== End Session ===", True)
        self.message_carrier.save_log_as_json()
        # 何か入力すると終了するメッセージを表示する。
        self.message_carrier.print_message_as_system("何か入力すると終了します。", False)
        await self.view.request_user_input()

        
    
    async def determine_objective(self, agent: BotAgent) -> tuple[str, str]:
        """
        実現可能な目的が設定されるまで、目的を尋ねる。
        """
        while True:
            objective = await self.ask_objective()
            context = await self.ask_context()
            feasibility = await self.feasibility_assessment(agent, objective, context)
            if not feasibility:
                text = f"Error: 達成不能と判断されました。\n目的設定からやり直してください。"
                self.message_carrier.print_message_as_system(text, True)
            else:
                text = f"達成可能と判定されました。タスクを生成します……"
                self.message_carrier.print_message_as_system(text, True)
                return objective, context


    async def feasibility_assessment(self, agent: BotAgent, objective: str, context: str) -> bool:
        """
        目的の実現可能性を判定する。
        """

        text = "目的の実現可能性を判定します……"
        self.message_carrier.print_message_as_system(text, True)

        abilities = self.file_reader.read_file("abilities.txt", "documents")
        prompt = f"""
        You are an AI that determines if the objective given by the user are feasible.
        You are part of a repository called AutoEvolver.
        AutoEvolver is capable of: 
        {abilities}
        Based on the above, determine whether or not the following objective is feasible.
        Response with a just simple "Yes" or "No”.
        Objective: {objective}
        Context: {context}
        Response: 
        """

        prompt_context = [{"role": Role.system.name, "content": prompt}]

        response = agent.response_to_context(prompt_context)
        self.view.process_event()
        if "Yes" in response:
            return True

        prompt_context.append({"role": Role.assistant.name, "content": response})
        prompt = f"""
        Please tell me why you have determined that this task is not feasible.
        Response:"""
        prompt_context.append({"role": Role.system.name, "content": prompt})
        response = agent.response_to_context(prompt_context)
        self.view.process_event()
        # responseを解決不能な理由として表示する
        text = f"Response: {response}"
        self.message_carrier.print_message_as_system(text, True)
        return False


    async def ask_objective(self) -> str:
        """
        ユーザーから、目的の設定の入力を受ける。
        """
        text = ("目的を入力してください。\n例：テトリスを作ってください。")
        self.message_carrier.print_message_as_system(text, True)
        
        try:
            objective = await self.view.request_user_input()
            self.view.process_event()
            if not objective:
                raise ValueError("目的が入力されていません。")
        except asyncio.CancelledError:
            raise
        
        text = "Objective: " + objective
        self.message_carrier.print_message_as_user(text, True)

        return objective
    

    async def ask_context(self) -> str:
        """
        ユーザーから、目的設定に関する文脈の入力を受ける。
        """
        text = ("目的に関する文脈を入力してください。\n例：Pythonで実行できる、シンプルなテトリス。音は必要ありません。")
        self.message_carrier.print_message_as_system(text, True)

        try:
            context = await self.view.request_user_input()
            self.view.process_event()
        except asyncio.CancelledError:
            raise
        text = "Context: " + context
        self.message_carrier.print_message_as_user(text, True)

        return context
                

    def split_to_tasks(self, agent: BotAgent, objective: str, context: str) -> list[Task]:
        prompt = f"""
        You are an AI listing tasks to be performed based on the following objective: {objective}.
        The context regarding the objective is as follows: {context}
        You are part of a repository called AutoEvolver and this objective must be resolved by AutoEvolver alone.
        Subdivide and list the objectives into tasks in order to resolve them. Do not try to solve them at this point.
        The list should be formatted with the "-" sign and should not include responses other than the list.
        Response:"""
        response = agent.response_to_prompt(prompt)
        self.view.process_event()
        tasks_text = response.split("\n") if "\n" in response else [response]
        # "-"から始まる行のみを抽出する
        tasks_text = [task for task in tasks_text if task.startswith("-")]

        # すべてのtasks_textをtaskに変換する
        tasks = [self.tasktext_to_task(agent, objective, context, task_text) for task_text in tasks_text]

        # 細分化前のTaskのリストを表示する。
        # リストは、TaskのContent - TaskTag.valueの順に表示される。
        # メッセージは一括で表示される
        self.message_carrier.print_message_as_system("=== Init Task List ===", True)
        print_text = ""
        for task in tasks:
            print_text += f"{task.content} - {task.tag.value}\n"
        self.message_carrier.print_message_as_system(print_text, True)

        # すべてのTaskを細分化するインフォメーションを出す
        self.message_carrier.print_message_as_system("=== Start Subdividing Tasks ===", True)

        # tasksの中から、subdividableなものを検索し、見つけるたびに細分化したリストとその要素を入れ替える
        # これを繰り返す
        # すべてのtasksがsubdividableでなくなったら、終了する
        new_tasks = tasks[:]
        while True:
            subdividable_tasks = [task for task in new_tasks if task.subdividable]
            if not subdividable_tasks:
                break
            for task in subdividable_tasks:
                subtasks = self.split_to_subtasks(agent, objective, context, task)
                task_index = new_tasks.index(task)
                new_tasks[task_index:task_index+1] = subtasks
        tasks = new_tasks

        # 細分化終了メッセージを出す
        self.message_carrier.print_message_as_system("=== Finish Subdividing Tasks ===", True)

        # 最終的なTasksのリストを表示する
        self.message_carrier.print_message_as_system("\n=== Confirmed Tasks ===", True)
        print_text = ""
        for task in tasks:
            print_text += f"{task.content} - {task.tag.value}\n"
        self.message_carrier.print_message_as_system(print_text, True)

        return tasks
    
    def split_to_subtasks(self, agent: BotAgent, objective: str, context: str, task: Task) -> list[Task]:
        """
        Taskをさらに小さなTaskに分割し、そのリストを返す。
        """
        prompt = f"""
        You are an AI that further subdivides the subdivided tasks to achieve the final objective {objective}.
        The context of the objective is {context}.
        You are part of a repository called AutoEvolver.
        The task to subdivide is {task.content}.
        The list should be formatted with the "-" sign and should not include responses other than the list.
        Response:"""
        response = agent.response_to_prompt(prompt)
        self.view.process_event()
        tasks_text = response.split("\n") if "\n" in response else [response]
        # "-"から始まる行のみを抽出する
        tasks_text = [task for task in tasks_text if task.startswith("-")]

        # すべてのtasks_textをtaskに変換する
        tasks = [self.tasktext_to_task(agent, objective, context, task_text) for task_text in tasks_text]

        # 細分化したTaskのリストを表示する。
        self.message_carrier.print_message_as_system("=== Subdivided Tasks ===", True)
        print_text = ""
        for task in tasks:
            print_text += f"{task.content} - {task.tag.value}\n"
        self.message_carrier.print_message_as_system(print_text, True)

        return tasks


    def tasktext_to_task(self, agent: BotAgent, objective: str, context: str, task_text: str) -> Task:
        prompt = f"""
        You are an AI that categorizes the solution to a given task as "ask user (1)", "output text by ChatGPT itself (2)", "run or write new Python module to solve (3)" "Further divide into smaller tasks (4)" or "unsolvable (0)".
        The task is part of the final objective {objective}. The context of that objective is {context}.
        The task is: {task_text}
        Select only one most appropriate number and return that number only. Any other response will not be included.
        If it is difficult to determine, just answer "4" for now.
        Number:"""
        response = agent.response_to_prompt(prompt)
        self.view.process_event()
        try:
            digit = response[0]
            number = int(digit)
        except ValueError:
            raise ValueError(f"response is not a number: {response} for {task_text}")
        # responseからタグを抽出する
        tag_dict = {
            0: TaskTag.unsolvable, 
            1: TaskTag.ask_user, 
            2: TaskTag.use_bot, 
            3: TaskTag.use_python,
            4: TaskTag.subdivide,
            }
        tag = tag_dict[number]
        task = Task(task_text, tag)
        return task
    

    def resolve_tasks(self, agent: BotAgent, objective: str, context: str, tasks: list[Task]) -> None:
        """
        tasksを解決する。
        """
        # すべてのtaskを解決する
        pass