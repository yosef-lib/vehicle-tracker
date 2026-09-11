from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse

import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "rahasia123")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import pandas as pd
import os

from app.database import engine, Base, get_db
from app import models

# Buat tabel database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vehicle Tracker API")

# Mount folder statis dan template HTML
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    # Data ringkasan (Mock/Sederhana)
    total_cost = 0
    recent_logs = db.query(models.FuelLog).order_by(models.FuelLog.date.desc()).limit(5).all()
    
    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request, 
        "title": "Dashboard Overview",
        "recent_logs": recent_logs,
        "total_cost": total_cost
    })

@app.get("/export")
async def export_excel(db: Session = Depends(get_db)):
    """Mengexport semua data log ke dalam file Excel"""
    # Ambil data dari database menggunakan Pandas
    fuel_logs = pd.read_sql(db.query(models.FuelLog).statement, db.bind)
    maint_logs = pd.read_sql(db.query(models.MaintenanceLog).statement, db.bind)
    
    file_path = "Laporan_Kendaraan.xlsx"
    
    # Tulis ke dalam file Excel dengan beberapa sheet
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        fuel_logs.to_excel(writer, sheet_name='Log_BBM', index=False)
        maint_logs.to_excel(writer, sheet_name='Log_Servis_Oli', index=False)
        
    return FileResponse(path=file_path, filename="Laporan_Kendaraan.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Endpoint CRUD Halaman lainnya (Kendaraan, Servis, Pajak)
@app.get("/vehicles", response_class=HTMLResponse)
async def vehicles_page(request: Request, db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).all()
    return templates.TemplateResponse(request=request, name="vehicles.html", context={"request": request, "title": "Kendaraan", "vehicles": vehicles})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
