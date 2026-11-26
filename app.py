import asyncio
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from indiaopt import NSEClient, BSEClient
app = FastAPI(title="SENSEX NIFTY Live Options API")
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_methods=["GET"],
   allow_headers=["*"],
)
# Cache prevents excessive exchange requests.
CACHE_SECONDS = 60
cache = {}
locks = {
   "bse": asyncio.Lock(),
   "nse": asyncio.Lock()
}

async def fetch_bse():
   async with BSEClient() as client:
       result = await client.fetch_option_chain(
           "999920",
           is_index=True
       )
       return result.to_dict()

async def fetch_nse():
   async with NSEClient() as client:
       result = await client.fetch_option_chain(
           "NIFTY",
           is_index=True
       )
       return result.to_dict()

async def get_data(exchange, fetch_function):
   now = time.time()
   if exchange in cache:
       saved_time, saved_data = cache[exchange]
       if now - saved_time < CACHE_SECONDS:
           return saved_data
   async with locks[exchange]:
       now = time.time()
       if exchange in cache:
           saved_time, saved_data = cache[exchange]
           if now - saved_time < CACHE_SECONDS:
               return saved_data
       try:
           data = await fetch_function()
           cache[exchange] = (time.time(), data)
           return data
       except Exception as error:
           raise HTTPException(
               status_code=502,
               detail=f"{exchange.upper()} data unavailable: {str(error)}"
           )

@app.get("/")
def home():
   return {
       "status": "running",
       "service": "SENSEX + NIFTY Options API"
   }

@app.get("/api/bse/sensex")
async def sensex():
   data = await get_data("bse", fetch_bse)
   return JSONResponse(content=jsonable_encoder(data))

@app.get("/api/nse/nifty")
async def nifty():
   data = await get_data("nse", fetch_nse)
   return JSONResponse(content=jsonable_encoder(data))
