from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .auth.security import verify_password, create_access_token, get_password_hash
from .auth.rbac import RoleChecker
from .agents.code_agent import ask_nexus_ops

app = FastAPI(title="NexusOps API")

fake_users_db = {
    "jr_dev": {
        "username": "junior_dev",
        "role": "junior_dev",
        "hashed_password": get_password_hash("jr_dev")
    },
    "sr_dev": {
        "username": "senior_dev",
        "role": "senior_dev",
        "hashed_password": get_password_hash("sr_dev")
    }
}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Issue token with the role
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/junior/tasks", dependencies=[Depends(RoleChecker(["junior_dev", "senior_dev"]))])
async def read_tasks():
    return {"message": "You can see this because you are at least a junior developer."}

@app.get("/senior/deploy", dependencies=[Depends(RoleChecker(["senior_dev"]))])
async def deploy_code():
    return {"message": "DANGER: Only senior developers can see this."}

@app.get("/ask", dependencies=[Depends(RoleChecker(["junior_dev", "senior_dev"]))])
async def ask_agent(question: str):
    answer = ask_nexus_ops(question)
    return {"answer": answer}