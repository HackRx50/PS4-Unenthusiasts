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
        
    def answer(self, question,session_id,document_id):
        msg_id = None
        context_messages=[]
        if session_id is not None:
            session_data = self.database.find_session_by_id(session_id)
            context_messages = session_data.get("context", [])
            
        system_prompt="""
             Identify where the query os the user is query or action
                Strictly follow the below output format
                Output format:
                {
                    "isQuery":Boolean,
                    "isAction": Boolean,
                    "query": String,
                    "action": String
                }
             
                isQuery should be true if the user query contains a question , 
                isAction should be true if the user query contains an action that they want to be performed 
                query should be the question that the user asked , **NOTE** you need to use context + current question to formulate a query for vector data base which will be used to query the knowledge base, it should be detailed and represnt clearly what user is asking with the help og current question + previous context messages
                action should be the action that the user wants to be performed
             
             """

        messages = [{"role": "system", "content": system_prompt}]
        for message in context_messages:
            messages.append({"role": "user", "content": message["query"]})
            messages.append({"role": "assistant", "content": message["gpt_response"]})

        messages.append({"role": "user", "content": question})
        res=self.llm.generate_response(messages=messages)
        res=json.loads(res)

        response = None
        if res["isQuery"]:
            response = self.kb.query_knowledge_base(res["query"],session_id,document_id)
        else:
            response={"gpt_response":"Action queued successfully"}

        if res["isAction"]:
            msg_id = str(uuid.uuid4())
            message=json.dumps({"user query":question,"response":response, "action":res["action"]})
            print(f"Sending message: {message}")
            self.messageQueue.publish_message(message,msg_id)
        print("RES",response)

        return {**response,"msg_id":msg_id}
    