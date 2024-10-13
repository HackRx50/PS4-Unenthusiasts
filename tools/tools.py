from langchain.tools import StructuredTool
from pydantic import BaseModel
from services.knowledgeBase import KnowledgeBaseService
from tools.todo import add_todo_item, list_todo_items, update_todo_item, delete_todo_item
from tools.order import eligibility_check, generate_leads, order,get_order_status,get_orders
from typing import Union
kb=KnowledgeBaseService("knowledgebase")

class KnowledgeBaseArgs(BaseModel):
    query: str
    # document_id: str
knowledge_base_tool = StructuredTool.from_function(
    name="SearchKnowledgeBase",
    func=kb.search_knowledge_base,
    description='Search the knowledge base for relevant information based on a detailed query from the user. Use this tool when placing order. i have product details in my knowledge base use them. Search only for what the user has asked for. Use the correct schema which is only query string thats it.',
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
  productId: Union[str, int]
  productName: str
  productPrice:float
  action: str
  mobile: str

order_tool = StructuredTool.from_function(
    name="Order",
    func=order,
    description='''Order or cancel a product from the store. Search details like id and price from knowledge base before doing this to get the proper values and then use them. if you dont have any of the arguements from schema, use NONE. Do not assume the fields.Pay attention to the schema, use  productId: str productName: str productPrice:float action: str. ONLY CALL this function if you have sufficient details.If productName is not specifies have it as None. STOP CHAIN AFTER THIS FUNCTION''',
    args_schema=orderArgs
)

class get_orderArgs(BaseModel):
  mobile: str

get_order_tool = StructuredTool.from_function(
    name="GetOrders",
    func=get_orders,
    description='Gets all the orders from the store for a user and returns it in detail including all the fields that are being returned upon successful execution of the function. Now check if the user needs anything else like placing order or get order status if yes then perform that action',
    args_schema=get_orderArgs
)

class orderStatusArgs(BaseModel):
    order_id: str
    mobile: str

order_status_tool = StructuredTool.from_function(
   name="OrderStatus",
   func=get_order_status,
    description='Get the status of the order.DONT CALL THIS UNLESS ASKED FOR IN THE question. you need to get all orders for this and check which order id is to be used from there, use context and users question as well.in order schema, order id is given as "id". order id is a string. it is in the format uuid',
)

generate_leads_tool = StructuredTool.from_function(
   name="GenerateLeads",
   func=generate_leads,
   description='Generate the leads and return the response which is being generated after execution of the function.',
)

eligibility_check_tool = StructuredTool.from_function(
   name="EligibilityCheck",
   func=eligibility_check,
   description='Check the eligibility and return True or False after execution of the function',
)
health_check_tool = StructuredTool.from_function(
   name="HealthCheck",
   func=eligibility_check,
   description='Check the health of the server and return True or False after execution of the function',
)


tools = [knowledge_base_tool, add_todo_tool, list_todo_tool, update_todo_tool, delete_todo_tool,order_tool,get_order_tool,order_status_tool,generate_leads_tool,eligibility_check_tool,health_check_tool]
