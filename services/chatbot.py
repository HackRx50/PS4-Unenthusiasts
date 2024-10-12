from services.llm import LLMService
from services.knowledgeBase import KnowledgeBaseService
from services.messageQueue import MessageQueueService
from services.contextDatabase import ContextDatabaseService
import json
import uuid

class Chatbot:
    def __init__(self,name):
        self.name = name
        self.llm = LLMService()
        self.kb=KnowledgeBaseService("knowledgebase")
        self.messageQueue = MessageQueueService(name, "localhost")
        self.database = ContextDatabaseService()
        
    def answer(self, question,session_id,document_id,user_id):
        msg_id = str(uuid.uuid4())
        context_messages=[]
        if session_id is not None:
            session_data = self.database.find_session_by_id(session_id)
            context_messages = session_data.get("context", [])
        if not session_id or not self.database.find_session_by_id(session_id):
            session_id = self.database.create_session(user_id)
        # system_prompt="""
        # **NOTE**: ONLY GIVE RESPONSE IN JSON. NOTHING ELSE.
        #      Identify where the question of the user is query or action
        #         Strictly follow the below output format
        #         Output format:
        #         {
        #             "isQuery":Boolean,
        #             "isAction": Boolean,
        #             "query": String,
        #             "action": String
        #         }
        #         query should be the question that the user asked , **NOTE** you need to use context + current question to formulate a query for vector data base which will be used to query the knowledge base, it should be detailed and represnt clearly what user is asking with the help of current question + previous context messages
        #         action should be the action that the user wants to be performed, this can be create/place an order, cancel order, get status- you will need id of the order for this so get all orders first then check for the order for which the user is asking status or use context as well, get all my orders
        #         if the user wants to place an order, then frame "action" where it first searches for the item in the knowledge base and then places order using these details
        #      """

        system_prompt = """
        **NOTE**: ONLY GIVE RESPONSE IN JSON. NOTHING ELSE.
        You are tasked with identifying whether the user's input is a query or an action. Use both the current input and previous context messages to formulate a detailed response. 
        Strictly adhere to the following format:
        {
            "isQuery": boolean(true or false),
            "isAction": boolean,
            "query": String,
            "action": String
        }
        Instructions:
        1. **isQuery**: True if the user input is a query, otherwise False.
        2. **isAction**: True if the user input is an action request (e.g., creating, canceling, or checking an order), otherwise False.
        3. **query**: Formulate a detailed query that clearly represents what the user is asking. Combine the current input and relevant context to create this query, as it will be used to query a vector database for the knowledge base.
        4. **action**: action can be like place an order, cancel order, check order status, get order status). frame the action which gives proper detail about what actions are to be performed and in which order
        - If the action requires an order (e.g., getting order status or canceling an order), retrieve the list of the user's orders first, then determine the specific order based on context or user input.
        - If the action involves placing an order, consider this while framing the action: first search the knowledge base for the requested item, then proceed with the order placement using the retrieved details.

        if the question doesnt fit properly in the above guidelines then you can say so. ensure proper guardrailing, dont give action if not stated proper

        Ensure the output follows the exact JSON format and is generated strictly based on the user’s input and context.
        """


        messages = [{"role": "system", "content": system_prompt}]
        context=[]

        for message in context_messages:
            messages.append({"role": "user", "content": message["query"]})
            messages.append({"role": "assistant", "content": message["gpt_response"]})
            context.append({"role": "user", "content": message["query"]})
            context.append({"role": "assistant", "content": message["gpt_response"]})

        messages.append({"role": "user", "content": question})
        res=self.llm.generate_response(messages=messages)
        print("this is res", res)
        res=json.loads(res)
        print("actionisthis : ",res["action"])

        response = None
        if res["isQuery"]:
            response = self.kb.query_knowledge_base(res["query"],msg_id,session_id,document_id,actual_query=question,context_messages=context)
        else:
            response={"gpt_response":"Action queued successfully"}

        if res["isAction"]:
            # msg_id = str(uuid.uuid4())
            message=json.dumps({"user query":question,"response":response, "action":res["action"]})
            print(f"Sending message: {message}")
            self.messageQueue.publish_message(message,msg_id,session_id)
        print("RES",response)

        return {**response,"msg_id":msg_id}
    