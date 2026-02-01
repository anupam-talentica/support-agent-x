from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Mock Server")


@app.get("/")
async def root():
    return {"message": "Mock server is running"}


@app.get("/health")
async def health():
    return {"status": {
        "components": [
            {
                "name": "dashboard",
                "health": "unhealthy",
                "reason": "chinmay deleted the dashboards"
            },
            {
                "name": "login",
                "health": "healthy",
                "reason": ""
            },
            {
                "name": "payment",
                "health": "unhealthy",
                "reason": "gateway timeout"
            },
            {
                "name": "profile",
                "health": "healthy",
                "reason": ""
            },
            {
                "name": "order",
                "health": "unhealthy",
                "reason": "database connection failed"
            },
            {
                "name": "location",
                "health": "healthy",
                "reason": ""
            }
        ]
    }}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
