from langchain.tools import StructuredTool
from pydantic import BaseModel
from services.knowledgeBase import KnowledgeBaseService
from tools.todo import add_todo_item, list_todo_items, update_todo_item, delete_todo_item
from tools.order import order,get_order_status,get_orders

kb=KnowledgeBaseService("knowledgebase")

class KnowledgeBaseArgs(BaseModel):
    query: str
    # document_id: str
knowledge_base_tool = StructuredTool.from_function(
    name="SearchKnowledgeBase",
    func=kb.search_knowledge_base,
    description='Search the knowledge base for relevant information based on a detailed query from the user. Use this tool when placing order. i have product details in my knowledge base use them.',
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


class orderArgs(BaseModel):
#   mobile: str
  productId: str
  productName: str
  productPrice:int
  action: str

order_tool = StructuredTool.from_function(
    name="Order",
    func=order,
    description='Order or cancel a product from the store. Use product details from knowledge base before doing this to get the proper details and then use them',
    args_schema=orderArgs
)



get_order_tool = StructuredTool.from_function(
    name="GetOrders",
    func=get_orders,
    description='Gets all the orders from the store for a user .',

)

order_status_tool = StructuredTool.from_function(
   name="OrderStatus",
   func=get_order_status,
    description='Get the status of the order',
)


tools = [knowledge_base_tool, add_todo_tool, list_todo_tool, update_todo_tool, delete_todo_tool,order_tool,get_order_tool,order_status_tool]
