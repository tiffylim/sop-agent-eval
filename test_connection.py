import anthropic

client = anthropic.Anthropic()  # automatically reads ANTHROPIC_API_KEY from the environment

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Say hello in one short sentence, and confirm you're ready to help build an agent."}
    ]
)

print(message.content[0].text)