import datetime
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fexa.scraper import scraper
from altline.scraper import scraper as altline_scraper
from w9_checker.main import lambda_handler

app = FastAPI()


@app.get("/fexa")
async def fexa():
    print("TEST")
    return StreamingResponse(
        iter([scraper().getvalue()]),
        media_type="application/x-zip-compressed",
        headers = { "Content-Disposition": f"attachment; filename=Fexa_data_{datetime.datetime.utcnow()}.zip"}
    )

@app.get("/altline")
async def altline():
    print("TEST")
    return StreamingResponse(
        iter([altline_scraper().getvalue()]),
        media_type="application/x-zip-compressed",
        headers = { "Content-Disposition": f"attachment; filename=Altline_data_{datetime.datetime.utcnow()}.zip"}
    )

@app.get("/w9_checker")
async def w9_checker(names: str):
    files = lambda_handler(names)
    return files


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)