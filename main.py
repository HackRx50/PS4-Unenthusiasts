from fastapi import FastAPI
from routes.chat import chat_router

app = FastAPI()

app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "API is running"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
