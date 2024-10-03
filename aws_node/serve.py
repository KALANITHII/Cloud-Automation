import os
import subprocess
import time

import boto3
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from main import graph

STS_TOKEN_TIME_LIMIT = int(os.environ.get("STS_TOKEN_TIME_LIMIT") or 3600)

credentials = {}

app = FastAPI()

# CORS settings
origins = ["http://localhost:0000", "https://hiaido.com", "http://localhost:0000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    user_query: str
    email: str


@app.get("/", summary="Root path", description="Root path to check if service is running")
async def root(request: Request):
    """
    Root path
    """
    return JSONResponse({"running": "yes", "agent": "multi"})


@app.get(
    "/health",
    summary="Health check path",
    description="Path used by orcestration services to check container health.",
)
async def health(request: Request):
    """
    Path used by orcestration services to check container health.
    """
    return JSONResponse({"healthy": True})


def get_credentials_from_db(email: str, owner: str):
    """
    Retrieves credentials associated with the provided email from DynamoDB.
    """
    session = boto3.Session(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION"),
    )
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table("account-factory-test")
    response = table.get_item(Key={"email": email, "owner": owner})
    if "Item" in response:
        sts_client = boto3.client("sts")
        assumed_role = sts_client.assume_role(
            RoleArn=response["Item"]["role_arn"],
            RoleSessionName="AssumeroleSession",
            DurationSeconds=STS_TOKEN_TIME_LIMIT,
        )
        assumed_role["Credentials"]["timestamp"] = time.time()
        print(assumed_role)
        return assumed_role["Credentials"]
    return None


def configure_aws_cli(aws_access_key_id, aws_secret_access_key, session_token, region, profile):
    subprocess.run(
        [
            "aws",
            "configure",
            "set",
            "aws_access_key_id",
            aws_access_key_id,
            "--profile",
            profile,
        ],
        check=True,
    )
    subprocess.run(
        [
            "aws",
            "configure",
            "set",
            "aws_secret_access_key",
            aws_secret_access_key,
            "--profile",
            profile,
        ],
        check=True,
    )
    subprocess.run(
        [
            "aws",
            "configure",
            "set",
            "aws_session_token",
            session_token,
            "--profile",
            profile,
        ],
        check=True,
    )
    subprocess.run(["aws", "configure", "set", "region", region, "--profile", profile], check=True)

    subprocess.run(["aws", "configure", "list", "--profile", profile], check=True)


def credentials_expired(email):
    if not credentials.get(email):
        return True
    else:
        current_timestamp = time.time()
        if current_timestamp < credentials.get(email)["timestamp"] + STS_TOKEN_TIME_LIMIT - 180:
            return False
        else:
            return True


async def check_cli_configured(request: Request):
    """
    Checks if CLI is configured before accessing certain endpoints.
    """
    data = await request.json()
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="User email required.")
    if not credentials.get(email):
        raise HTTPException(
            status_code=400,
            detail="CLI not configured. Please configure the CLI before accessing this endpoint.",
        )
    if credentials_expired(email):
        print("CREDENTIALS EXPIRED")
        raise HTTPException(
            status_code=400,
            detail="Session expired. CLI not configured. Please configure the CLI before accessing this endpoint.",
        )
    return True


# TODO authenticate user
@app.post(
    "/configure-cli",
    summary="Configure CLI",
    description="Configures the CLI with the credentials associated with the provided email.",
)
async def configure_cli(request: Request):
    """
    Configures the CLI with credentials associated with the provided email.
    """
    try:
        data = await request.json()
        email = data.get("email")
        owner = data.get("owner")
        print(email, owner)

        if not email:
            raise HTTPException(status_code=400, detail="email parameter is required")
        if not owner:
            raise HTTPException(status_code=400, detail="owner parameter is required")
        global credentials
        if credentials.get(email) and not credentials_expired(email):
            return JSONResponse({"status": "CLI_ALREADY_CONFIGURED"})
        credentials[email] = get_credentials_from_db(email, owner)
        if credentials.get(email):
            access_key_id = credentials[email]["AccessKeyId"]
            secret_access_key = credentials[email]["SecretAccessKey"]
            session_token = credentials[email]["SessionToken"]
            configure_aws_cli(
                access_key_id,
                secret_access_key,
                session_token,
                "us-east-1",
                email,
            )
            return JSONResponse({"status": "CLI configured successfully"})
    except Exception as e:
        print(e.with_traceback())
        raise HTTPException(status_code=500, detail=str(e))


chat_history = []


@app.post(
    "/chat",
    summary="Process Query",
    description="Processes a user query and returns a response from the AWS Agent.",
    dependencies=[Depends(check_cli_configured)],
)
async def process_query(query: Query):
    try:
        # TODO: use some other method tp set current profile
        os.environ["CURRENT_PROFILE"] = query.email

        chat_history.append({"role": "user", "content": query.user_query})
        response = graph.invoke(chat_history[-5:])
        output = response[-1].content
        chat_history.append({"role": "assistant", "content": output})
        return JSONResponse({"response": output})
    except Exception as e:
        print(e.with_traceback())
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "serve:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT") or 8000),
        reload=True,
    )
