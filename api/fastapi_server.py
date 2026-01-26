#uvicorn fastapi_server:app
# rEgdtkQLFPm58iYW databas lösenord


from fastapi import FastAPI

app = FastAPI()
@app.get("/") # Define a GET endpoint at the root URL
def root():
    return {"Det fungerar"} # Return a simple JSON response indicating that the server is working