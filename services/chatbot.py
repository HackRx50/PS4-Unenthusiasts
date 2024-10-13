from services.llm import LLMService
from services.knowledgeBase import KnowledgeBaseService
from services.messageQueue import MessageQueueService
from services.contextDatabase import ContextDatabaseService
from services.actions import ActionExecuter
import json
import uuid

class Chatbot:
    def __init__(self,name):
        self.name = name
        self.llm = LLMService()
        self.kb=KnowledgeBaseService("knowledgebase")
        self.messageQueue = MessageQueueService(name, "localhost")
        self.database = ContextDatabaseService()
        self.actionExecutor= ActionExecuter()
        
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
        **NOTE**: ONLY GIVE RESPONSE IN JSON. NOTHING ELSE. DONT WRITE "```" in the output. JUST PROVIDE JSON OBJECT
        You are tasked with identifying whether the user's input is a query or an action. Use both the current input and previous context messages to formulate a detailed response. 
        Strictly adhere to the following format:
        {
            "isQuery": boolean(true or false),
            "isAction": boolean,
            "query": String,
            "action": String,
            "extra":String
            error:String
        }
        Instructions:
        1. **isQuery**: true if the user input is a query, otherwise false.
        2. **isAction**: true if the user input is an action request (e.g., creating, canceling, or checking an order), otherwise false.
        3. **query**: Formulate a detailed query that clearly represents what the user is asking. Combine the current input and relevant context to create this query, as it will be used to query a vector database for the knowledge base.
        4. **action**: action can only be place an order, cancel order, check order status, get order status). Formulate a detailed action that clearly represents what the user is asking. Combine the current input and relevant context to create this action query, as it will be used to query a vector database for the knowledge base.
        - If the action requires an order (e.g., getting order status or canceling an order), retrieve the list of the user's orders first, then determine the specific order based on context or user input.
        - If the action involves placing an order, frame the action by mentioning everything in correct order: first search the knowledge base for the requested item, then proceed with the order placement using the retrieved details. If the requested item is not mentioned then check the context messages of previous chat to find out what item is being talked about

        if the question doesnt fit properly in the above guidelines then you can say so. ensure proper guardrailing, dont give action if not stated properly.
        if the question is neither query nor action then write its response in "extra" which could be you being a friendly bot, dont answer any queries that are out of context here, just say ask related to the documents uploaded or ask me to perform actions. otherwise leave it blank
        if  the action is for creating an order and it doesnt provide a name for document add {"error:<error>}
        if  the action is for requesting to check status an order and it doesnt provide which order add {"error:<error>}

        Ensure the output follows the exact JSON format and is generated strictly based on the user’s input and context. DONT WRITE "```" in the output
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
        if res["error"]:
            self.database.update_session_context(session_id, {
            "query": question,
            "gpt_response": res["error"],
            })
            return {"gpt_response": res["error"], "session_id": session_id}
        
            print("ERROR1: ",res["error"])
            response = {"gpt_response":res["error"]}
        if res["isQuery"]:
            response = self.kb.query_knowledge_base(res["query"],msg_id,session_id,document_id,actual_query=question,context_messages=context)
        elif res["isAction"]:
            response={"gpt_response":"Action queued successfully"}
        else:
            # response={"gpt_response":"Hello, please ask either queries based on your uploaded documents or ask me to perform one of the following actions: place order, get orders, get order status"}
            response={"gpt_response":res["extra"]}

        if res["isAction"]:
            # msg_id = str(uuid.uuid4())
            message = f"""This is user query: {res["action"]}"""
            
            if response is not None and res["isQuery"]:
                message += f"""This is the previous response context: {response["gpt_response"]}"""
            
            print(f"Sending message: {message}")
            
            actionRes = self.actionExecutor.sync_executor(message,user_id)
            
            # Handle the case where actionRes is None or empty
            if actionRes:
                response["action_response"] = actionRes
            else:
                response["action_response"] = "No action response received."  # Set a default message or handle the case accordingly
            
        print("RESPONSE", response)

        self.database.update_session_context(session_id, {
            "query": question,
            "gpt_response": json.dumps({
                "query_response": response.get("gpt_response", "No query response available"),
                "action_response": response.get("action_response", "No action response available")
            }),
        })

        return {
            "gpt_response": json.dumps({
                "query_response": response.get("gpt_response", "No query response available"),
                "action_response": response.get("action_response", "No action response available")
            }),
            "session_id": session_id,
        }


        # if res["isAction"]:
        #     # msg_id = str(uuid.uuid4())
        #     message=f"""This is user query: {res["action"]}"""
        #     if response is not None and res["isQuery"]:
        #         message+=f"""This is the previous response context : {response["gpt_response"]}"""
      
        #     print(f"Sending message: {message}")
        #     actionRes=self.actionExecutor.sync_executor(message)
        #     response["action_response"]=actionRes
        # print("RESPONSE",response)

        # self.database.update_session_context(session_id, {
        #     "query": question,
        #     "gpt_response": json.dumps({
        #         "query_response": response["gpt_response"],
        #         "action_response": response["action_response"]
        #     }),
        # })

        # return {"gpt_response": json.dumps({
        #         "query_response": response["gpt_response"],
        #         "action_response": response["action_response"]
        #     }),
        #     "session_id": session_id,
        #     }


# "suggested":array of strings,
#         5. suggest better questions which suit the context or possible follow up questions that he might have? suggest 4 of them.
    