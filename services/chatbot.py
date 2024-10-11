from services.llm import LLMService
from services.knowledgeBase import KnowledgeBaseService
from services.messageQueue import MessageQueueService
import json
import uuid

class Chatbot:
    def __init__(self,name):
        self.name = name
        self.llm = LLMService()
        self.kb=KnowledgeBaseService("knowledgebase")
        self.messageQueue = MessageQueueService(name, "localhost")
        
    def answer(self, question,session_id,document_id):
        msg_id = None
        res=self.llm.generate_response(messages=[
            {"role": "system", "content": """
             Identify where the query os the user is query or action
                Strictly follow the below output format
                Output format:
                {
                    "isQuery":Boolean,
                    "isAction": Boolean,
                    "query": String,
                    "action": String
                }
             
                isQuery should be true if the user query contains a question 
                isAction should be true if the user query contains an action that they want to be performed
                query should be the question that the user asked
                action should be the action that the user wants to be performed
             
             """},
            {"role": "user", "content": question}
        ])
        res=json.loads(res)

        response = None
        if res["isQuery"]:
            response = self.kb.query_knowledge_base(res["query"],session_id,document_id)
        else:
            response="Action queued successfully"

        if res["isAction"]:
            msg_id = str(uuid.uuid4())
            message=json.dumps({"user query":question,"response":response, "action":res["action"]})
            print(f"Sending message: {message}")
            self.messageQueue.publish_message(message,msg_id)

        return {"result":response,"msg_id":msg_id}
    