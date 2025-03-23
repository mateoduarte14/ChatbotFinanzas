from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel

api_key = "AIzaSyCNBtkNKlAiyljGglYUFja4QKl27EKnfwc"

modelo = LiteLLMModel(
    
    api_key=api_key,
    model_id="gemini/gemini-2.0-flash-thinking-exp-01-21"
)

agent = CodeAgent(
    model=modelo,
    tools=[DuckDuckGoSearchTool()]

)

agent.run("Que dia es hoy ")