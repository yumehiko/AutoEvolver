from .role import Role
import openai

class BotAgent:
    """
    要求に応じたテキストを返す、柔軟なChatBotエージェント。
    """

    def response_to_prompt(self, prompt: str, role: Role = Role.system, model: str = "gpt-3.5-turbo") -> str:
        """
        promptに対する応答を取得する。
        """
        persona_message = {"role": role.name, "content": prompt}

        response_data = openai.ChatCompletion.create(  # type: ignore[no-untyped-call]
            model=model,
            messages=[persona_message],
        )

        response: str = response_data["choices"][0]["message"]["content"]
        return response
    
    def response_to_context(self, context: list[dict[str, str]], model: str = "gpt-3.5-turbo") -> str:
        """
        contextに対して応答を返す。
        """
        response_data = openai.ChatCompletion.create(  # type: ignore[no-untyped-call]
            model=model,
            messages=context,
        )

        response: str = response_data["choices"][0]["message"]["content"]
        return response