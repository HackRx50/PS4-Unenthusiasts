import certifi
import pika
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.agents import initialize_agent,AgentType
import json
from pymongo import MongoClient
from services.messageQueue import MessageQueueService
from services.llm import LLMService
from tools.tools import tools
from langchain_core.prompts import PromptTemplate
from settings import Settings
env=Settings()
MONGO_URI = env.mongo_uri
MONGO_DB_NAME=env.mongo_db_name
from langchain_community.llms import OpenAI
OPENAI_API_KEY = env.openai_api_key

template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

prompt = PromptTemplate.from_template(template)


class ContextDatabaseService:
    def __init__(self):
        self.client = MongoClient(MONGO_URI,tlsCAFile=certifi.where())
        self.db = self.client[MONGO_DB_NAME]
        self.logs_collection = self.db["logs"]

    def save_log(self, message_id, combined_output):
        log_data = {
            "_id": message_id,
            "output": combined_output
        }
        print("saving in db")
        # self.logs_collection.insert_one(log_data)
        result = self.logs_collection.insert_one(log_data)
        if result.inserted_id:
            print(f"Log with ID: {message_id} saved successfully in MongoDB.")
        else:
            print(f"Failed to save log with ID: {message_id}.")
    
    def get_log_by_id(self, message_id):
        return self.logs_collection.find_one({"_id": message_id})

    def update_session_context(self, session_id: str, message_id: str, combined_output: dict):
    # Update the context array where msg_id matches message_id and set actionresponse
        return self.db.sessions.update_one(
            {"_id": session_id, "context.msg_id": message_id},
            {"$set": {"context.$.actionresponse": combined_output}}
        )



class ActionExecuter:
    def __init__(self):
        pass
        # self.message_queue = MessageQueueService(chatbotName,"localhost")
        # self.num_workers = num_workers
        self.llm = OpenAI(openai_api_key=OPENAI_API_KEY)
        # self.db_service = ContextDatabaseService()  
        self.tools = tools 
        self.llmservice=LLMService()
        # self.executor = ThreadPoolExecutor(max_workers=self.num_workers)  
    

    # def on_message(self, ch, method, properties, body):
    #     # future = self.executor.submit(self.process_message, body,properties)
    #     # future.add_done_callback(lambda x:
    #     #     print(f"Task completed: {x.result()}"))
    #     ch.basic_ack(delivery_tag=method.delivery_tag) 
    #     self.process_message(body,properties)
        
        

    # def process_message(self, body,properties):
    #     if isinstance(body, bytes):
    #         body = body.decode("utf-8")  # Decode from bytes to string
    #         body = json.loads(body)  
    #     reactquery = body["action"]
    #     print(f"Received message: {reactquery} {type(reactquery)}")

    #     agent = initialize_agent(
    #         tools=self.tools,
    #         llm=self.llm,
    #         verbose=True,
    #         agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    #         max_iterations=2
    #     )
    #     captured_output = []
    #     response= agent.run(reactquery)
            

        
    #     # self.db_service.save_log(properties.message_id, combined_output)
    #     session_id = properties.headers.get("session_id") if properties.headers else None



    #     # response = agent.run(body)
    #     # print(f"Processed message: {response}")

    #     return response 
        

    # def start_consuming(self):
    #     self.message_queue.consume_message( callback=self.on_message)
    #     print(f"Listening for messages on queue with {self.num_workers} workers...")

        

    # def stop_consuming(self):
    #     if self.connection:
    #         self.connection.close()


    def sync_executor(self, reactquery):
        try:
            print("react query:", reactquery)
            agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                verbose=True,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                max_iterations=2
            )
            response_stream = agent.stream(reactquery)
            response = []
            
            for message_chunk in response_stream:
                print("message chunk:", message_chunk)
                response.append(message_chunk)  # Correctly appending chunks to the list
            
            combined_output = ''.join([str(chunk) for chunk in response])

            # Generate a concise response using llmservice
            res = self.llmservice.generate_response(messages=[
                {
                    "role": "user",
                    "content": f"This is the user query: {reactquery}\n"
                            f"This is the complete log of the agent executing the task for the query:\n"
                            f"{combined_output}\n\n"
                            "I want you to provide a concise response. "
                            "**NOTE**: All data points should be included."
                }
            ])
            
            print(res)
            return res

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
