from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import os
import secrets
from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.database import engine, Base, get_db
from app import models

# Buat tabel database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vehicle Tracker API")

# Setup Auth
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

# Mount folder statis dan template HTML
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    recent_logs = db.query(models.FuelLog).order_by(models.FuelLog.date.desc()).limit(5).all()
    # Hitung total cost
    fuel_cost = db.query(func.sum(models.FuelLog.cost)).scalar() or 0
    maint_cost = db.query(func.sum(models.MaintenanceLog.cost)).scalar() or 0
    total_cost = fuel_cost + maint_cost
    
    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request, 
        "title": "Dashboard Overview",
        "recent_logs": recent_logs,
        "total_cost": total_cost
    })



@app.post("/vehicles/add")
async def add_vehicle(
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    license_plate: str = Form(""),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    new_v = models.Vehicle(name=name.lower(), type=type, license_plate=license_plate)
    db.add(new_v)
    db.commit()
    return RedirectResponse(url="/vehicles", status_code=303)

@app.get("/vehicles"
, response_class=HTMLResponse)
async def vehicles_page(request: Request, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    vehicles = db.query(models.Vehicle).all()
    return templates.TemplateResponse(request=request, name="vehicles.html", context={
        "request": request, "title": "Data Kendaraan", "vehicles": vehicles
    })

@app.get("/fuel", response_class=HTMLResponse)
async def fuel_page(request: Request, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    logs = db.query(models.FuelLog).order_by(models.FuelLog.date.desc()).all()
    return templates.TemplateResponse(request=request, name="fuel.html", context={
        "request": request, "title": "Riwayat BBM", "logs": logs
    })

@app.get("/maintenance", response_class=HTMLResponse)
async def maintenance_page(request: Request, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    logs = db.query(models.MaintenanceLog).order_by(models.MaintenanceLog.date.desc()).all()
    return templates.TemplateResponse(request=request, name="maintenance.html", context={
        "request": request, "title": "Servis & Oli", "logs": logs
    })

@app.get("/tax", response_class=HTMLResponse)
async def tax_page(request: Request, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    # Untuk sementara, tax bisa ngambil dari MaintenanceLog category 'Pajak'
    logs = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.category == 'Pajak').order_by(models.MaintenanceLog.date.desc()).all()
    return templates.TemplateResponse(request=request, name="tax.html", context={
        "request": request, "title": "Data Pajak", "logs": logs
    })

@app.get("/export")
async def export_excel(db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    fuel_logs = pd.read_sql(db.query(models.FuelLog).statement, db.bind)
    maint_logs = pd.read_sql(db.query(models.MaintenanceLog).statement, db.bind)
    
    file_path = "Laporan_Kendaraan.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        fuel_logs.to_excel(writer, sheet_name='Log_BBM', index=False)
        maint_logs.to_excel(writer, sheet_name='Log_Servis_Oli', index=False)
        
    return FileResponse(path=file_path, filename="Laporan_Kendaraan.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.get("/delete/{table}/{id}")
async def delete_record(request: Request, table: str, id: int, db: Session = Depends(get_db), username: str = Depends(get_current_user)):
    if table == "fuel":
        record = db.query(models.FuelLog).filter(models.FuelLog.id == id).first()
    elif table == "maintenance":
        record = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.id == id).first()
    elif table == "vehicle":
        record = db.query(models.Vehicle).filter(models.Vehicle.id == id).first()
        
    if record:
        db.delete(record)
        db.commit()
    
    url = f"/{table}s" if table == "vehicle" else f"/{table}"
    return RedirectResponse(url=url, status_code=303)

@app.post("/fuel/edit/{id}")
async def edit_fuel(
    request: Request, id: int, 
    date: str = Form(...), fuel_type: str = Form(...), 
    volume: float = Form(...), cost: int = Form(...), odometer: int = Form(...),
    db: Session = Depends(get_db), username: str = Depends(get_current_user)
):
    record = db.query(models.FuelLog).filter(models.FuelLog.id == id).first()
    if record:
        record.date = datetime.strptime(date, "%Y-%m-%d").date()
        record.fuel_type = fuel_type
        record.volume_liters = volume
        record.cost = cost
        record.odometer = odometer
        db.commit()
    return RedirectResponse(url="/fuel", status_code=303)

@app.post("/maintenance/edit/{id}")
async def edit_maintenance(
    request: Request, id: int, 
    date: str = Form(...), category: str = Form(...), 
    description: str = Form(...), cost: int = Form(...),
    db: Session = Depends(get_db), username: str = Depends(get_current_user)
):
    record = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.id == id).first()
    if record:
        record.date = datetime.strptime(date, "%Y-%m-%d").date()
        record.category = category
        record.description = description
        record.cost = cost
        db.commit()
    return RedirectResponse(url="/maintenance", status_code=303)
