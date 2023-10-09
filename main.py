import datetime

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fexa.scraper import scraper

app = FastAPI()


@app.get("/fexa")
async def fexa_scraper():
    return StreamingResponse(
        iter([scraper().getvalue()]),
        media_type="application/x-zip-compressed",
        headers = { "Content-Disposition": f"attachment; filename=Fexa_data_{datetime.datetime.utcnow()}.zip"}
    )

