from fastapi import FastAPI

app = FastAPI(title="LingoLift Backend")

@app.get("/")
def root():
    return{"message":"Welcome to the LingoLift Backend"}