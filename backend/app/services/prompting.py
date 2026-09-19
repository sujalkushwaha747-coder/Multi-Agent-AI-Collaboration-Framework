def render_prompt(system_message: str, user_message: str) -> str:
    try:
        from langchain_core.prompts import ChatPromptTemplate

        template = ChatPromptTemplate.from_messages(
            [("system", system_message), ("human", "{user_message}")]
        )
        messages = template.format_messages(user_message=user_message)
        return "\n\n".join(f"{message.type.upper()}: {message.content}" for message in messages)
    except Exception:
        return f"SYSTEM:\n{system_message}\n\nUSER:\n{user_message}"

