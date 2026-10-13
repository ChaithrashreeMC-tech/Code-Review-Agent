from fastapi import FastAPI, Depends

app = FastAPI()

def get_database_session():
    return "db_session"

@app.get("/data/violation")
async def fetch_data_direct_global():
    # Violation: Directly instantiates or uses global connection without Depends()
    db = get_database_session()
    return {"data": db}

@app.get("/data/safe")
async def fetch_data_injected(db=Depends(get_database_session)):
    # Safe: Uses FastAPI Depends() for clean dependency injection
    return {"data": db}

