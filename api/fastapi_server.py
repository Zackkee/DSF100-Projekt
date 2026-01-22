#uvicorn fastapi_server:app
# rWYRx4lEoHYbc5sA databas lösenord
#hejsan

from fastapi import FastAPI

app = FastAPI()
@app.get("/") # Define a GET endpoint at the root URL
def root():
    return {"Det fungerar"} # Return a simple JSON response indicating that the server is working