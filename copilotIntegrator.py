import asyncio
from copilot import CopilotClient
from copilot.session import PermissionHandler

def promptBuilder(topic) -> str:
    prompt: str = 'return a markdown document with 10 multiple choice trivia questions on ' + topic
    return prompt



async def queryer(prompt: str) -> str:
    print('starting Copilot SDK client...')
    client = CopilotClient()
    await client.start()
    session = await client.create_session(
        on_permission_request=PermissionHandler.approve_all,
        model="auto"
    )
    response = await session.send_and_wait(prompt)
    content: str = response.data.content
    await client.stop() 
    print('SDK client closed.')
    return content

print(promptBuilder('Robert Pattinson Movies'))
response: str = asyncio.run(queryer(promptBuilder('Robert Pattinson Movies')))
with open(r'U:\PY2026f\triviaProgram\TriviaProgram\RobertPQuestions.md', "w", encoding = 'utf-8') as file:
    file.write(str(response))
print('write completed')
