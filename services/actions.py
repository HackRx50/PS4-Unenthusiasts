import pika
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.agents import initialize_agent,AgentType
import json
from services.messageQueue import MessageQueueService
from services.llm import LLMService
from tools.tools import tools
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI


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




class ActionExecuter:
    def __init__(self, chatbotName,num_workers):
        self.message_queue = MessageQueueService(chatbotName,"localhost")
        self.num_workers = num_workers
        self.llm = OpenAI()

        self.tools = tools 
        self.executor = ThreadPoolExecutor(max_workers=self.num_workers)  
    

    def on_message(self, ch, method, properties, body):
        future = self.executor.submit(self.process_message, body)
        future.add_done_callback(lambda x:
            print(f"Task completed: {x.result()}"))
        
        ch.basic_ack(delivery_tag=method.delivery_tag) 

    def process_message(self, body):
        print(f"Received message: {body}")


        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            verbose=True,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        )

        response = agent.run(body)
        print(f"Processed message: {response}")

    def start_consuming(self):
        self.message_queue.consume_message( callback=self.on_message)
        print(f"Listening for messages on queue with {self.num_workers} workers...")

        

    def stop_consuming(self):
        if self.connection:
            self.connection.close()
