from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import chat_router
from routes.auth import auth_router
import multiprocessing
import uvicorn
from services.actions import ActionExecuter  

app = FastAPI()
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow these origins
    allow_credentials=True,  # Allow credentials such as cookies
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(chat_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "API is running"}

def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def start_action_executer():
    chatbot_name = "chatbot"
    num_workers = 5  
    action_executer = ActionExecuter(chatbot_name, num_workers)
    
    action_executer.start_consuming()  

if __name__ == "__main__":
    fastapi_process = multiprocessing.Process(target=start_fastapi)
    action_executer_process = multiprocessing.Process(target=start_action_executer)

    fastapi_process.start()
    action_executer_process.start()

    fastapi_process.join()
    action_executer_process.join()
