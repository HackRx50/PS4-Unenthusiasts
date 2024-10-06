from langchain.tools import StructuredTool
from pydantic import BaseModel
from services.knowledgeBase import KnowledgeBaseService
from tools.todo import add_todo_item, list_todo_items, update_todo_item, delete_todo_item


kb=KnowledgeBaseService("knowledge_base")

class KnowledgeBaseArgs(BaseModel):
    query: str
knowledge_base_tool = StructuredTool.from_function(
    name="SearchKnowledgeBase",
    func=kb.search_knowledge_base,
    description='Search the knowledge base for relevant information based on a detailed query from the user.',
    args_schema=KnowledgeBaseArgs
)

add_todo_tool = StructuredTool.from_function(
    name="AddToDo",
    func=add_todo_item,
    description="Add a new item to your to-do list. Input should be the to-do item."
)

list_todo_tool = StructuredTool.from_function(
    name="ListToDo",
    func=list_todo_items,
    description="List all items in your to-do list."
)

class UpdateToDoItemArgs(BaseModel):
    item_id: int
    new_item: str

update_todo_tool = StructuredTool.from_function(
    name="UpdateToDo",
    func=update_todo_item,
    description='Update an existing to-do item.',
    args_schema=UpdateToDoItemArgs,
)

delete_todo_tool = StructuredTool.from_function(
    name="DeleteToDo",
    func=lambda todo_id: delete_todo_item(int(todo_id)),
    description="Delete a to-do item. Input should be the to-do item ID."
)

tools = [knowledge_base_tool, add_todo_tool, list_todo_tool, update_todo_tool, delete_todo_tool]
