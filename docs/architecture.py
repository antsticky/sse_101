from diagrams import Diagram
from diagrams.programming.framework import React
from diagrams.programming.framework import FastAPI
from diagrams.onprem.inmemory import Redis
from diagrams.generic.compute import Rack

with Diagram("SSE Job Architecture", show=False, filename="architecture", outformat="png"):
    fe = React("Frontend (React)")
    be1 = FastAPI("BE1 Gateway\n(FastAPI)")
    be2 = Rack("BE2 Worker\n(async jobs)")
    redis = Redis("Redis\nState + Queue")

    fe >> be1
    be1 >> redis
    redis >> be2
    be2 >> redis
    be1 << fe
