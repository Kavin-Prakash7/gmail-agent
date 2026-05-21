class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func

    async def execute(self, name, **kwargs):
        if name in self.tools:
            return await self.tools[name](**kwargs)
        raise ValueError(f"Tool {name} not found")

registry = ToolRegistry()

# Register basic tools
async def gmail_read_tool(message_id):
    return {"status": "read", "message_id": message_id}

registry.register("gmail_read", gmail_read_tool)
