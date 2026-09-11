import os

main_code = """from fastapi import FastAPI, Request, Depends
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

@app.get("/vehicles", response_class=HTMLResponse)
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
"""

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)


# Create modern HTML files with animations
html_files = {
    "vehicles.html": """{% extends "base.html" %}
{% block content %}
<div x-data="{ show: false }" x-init="setTimeout(() => show = true, 100)">
    <div x-show="show" x-transition.opacity.duration.800ms x-transition:enter-start="opacity-0 translate-y-4" x-transition:enter-end="opacity-100 translate-y-0" class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">Daftar Kendaraan</h2>
        <button class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg font-medium shadow-lg shadow-blue-500/30 transform hover:scale-105 transition-all duration-300">
            <i class="fa-solid fa-plus mr-2"></i> Tambah Kendaraan
        </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% if vehicles %}
            {% for v in vehicles %}
            <div x-show="show" x-transition.opacity.duration.1000ms.delay.{{ loop.index0 * 100 }}ms x-transition:enter-start="opacity-0 scale-95" x-transition:enter-end="opacity-100 scale-100" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                <div class="flex justify-between items-start mb-4">
                    <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/40 group-hover:rotate-6 transition-transform duration-300">
                        <i class="fa-solid fa-motorcycle text-2xl"></i>
                    </div>
                    <span class="px-3 py-1 bg-emerald-100 text-emerald-600 rounded-full text-xs font-bold tracking-wide">Aktif</span>
                </div>
                <h3 class="text-xl font-bold text-gray-800 mb-1 capitalize">{{ v.name }}</h3>
                <p class="text-gray-500 text-sm mb-4"><i class="fa-regular fa-id-card mr-1"></i> ID Kendaraan: #{{ v.id }}</p>
                
                <div class="border-t border-gray-100 pt-4 flex justify-between items-center">
                    <button class="text-blue-600 font-medium hover:text-blue-700 text-sm"><i class="fa-solid fa-chart-line mr-1"></i> Statistik</button>
                    <button class="text-gray-400 hover:text-red-500 transition-colors"><i class="fa-solid fa-trash"></i></button>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="col-span-full bg-white p-12 rounded-2xl border border-dashed border-gray-300 flex flex-col items-center justify-center text-center">
                <div class="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center text-gray-400 text-3xl mb-4 shadow-inner">
                    <i class="fa-solid fa-motorcycle"></i>
                </div>
                <h3 class="text-lg font-bold text-gray-700 mb-2">Belum Ada Kendaraan</h3>
                <p class="text-gray-500 max-w-sm">Kirim pesan pengeluaran lewat Bot Telegram, dan kendaraan akan otomatis terdaftar di sini!</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}""",

    "fuel.html": """{% extends "base.html" %}
{% block content %}
<div x-data="{ show: false }" x-init="setTimeout(() => show = true, 100)">
    <div x-show="show" x-transition.opacity.duration.800ms class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden transform transition-all">
        <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-gray-50 to-white">
            <h3 class="text-lg font-bold text-gray-800"><i class="fa-solid fa-gas-pump text-blue-500 mr-2"></i> Riwayat Pengisian BBM</h3>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-gray-50/50 text-gray-500 text-xs uppercase tracking-wider">
                        <th class="p-4 font-medium">Tanggal</th>
                        <th class="p-4 font-medium">Kendaraan</th>
                        <th class="p-4 font-medium">Volume & Jenis</th>
                        <th class="p-4 font-medium">Biaya (Rp)</th>
                        <th class="p-4 font-medium">Odometer</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-sm">
                    {% if logs %}
                        {% for log in logs %}
                        <tr class="hover:bg-blue-50/50 transition-colors group cursor-default">
                            <td class="p-4 text-gray-600">{{ log.date }}</td>
                            <td class="p-4 font-medium text-gray-800 capitalize">Vario (ID: {{ log.vehicle_id }})</td>
                            <td class="p-4 font-medium">
                                <span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg text-xs mr-2">{{ log.volume_liters }} L</span> 
                                <span class="capitalize text-gray-600">{{ log.fuel_type }}</span>
                            </td>
                            <td class="p-4 font-bold text-gray-800 group-hover:text-blue-600 transition-colors">Rp {{ "{:,}".format(log.cost) }}</td>
                            <td class="p-4 text-gray-500"><i class="fa-solid fa-gauge-high mr-1"></i>{{ "{:,}".format(log.odometer) }} KM</td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="5" class="p-8 text-center text-gray-400">Tidak ada data.</td></tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}""",

    "maintenance.html": """{% extends "base.html" %}
{% block content %}
<div x-data="{ show: false }" x-init="setTimeout(() => show = true, 100)">
    <div x-show="show" x-transition.opacity.duration.800ms class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden transform transition-all">
        <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-gray-50 to-white">
            <h3 class="text-lg font-bold text-gray-800"><i class="fa-solid fa-wrench text-orange-500 mr-2"></i> Log Servis & Oli</h3>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-gray-50/50 text-gray-500 text-xs uppercase tracking-wider">
                        <th class="p-4 font-medium">Tanggal</th>
                        <th class="p-4 font-medium">Kategori</th>
                        <th class="p-4 font-medium">Keterangan</th>
                        <th class="p-4 font-medium">Biaya (Rp)</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-sm">
                    {% if logs %}
                        {% for log in logs %}
                        <tr class="hover:bg-orange-50/50 transition-colors group">
                            <td class="p-4 text-gray-600">{{ log.date }}</td>
                            <td class="p-4 font-medium text-gray-800">
                                <span class="bg-orange-100 text-orange-700 px-3 py-1 rounded-lg text-xs capitalize">{{ log.category }}</span>
                            </td>
                            <td class="p-4 text-gray-600 capitalize">{{ log.description }}</td>
                            <td class="p-4 font-bold text-gray-800 group-hover:text-orange-600 transition-colors">Rp {{ "{:,}".format(log.cost) }}</td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="4" class="p-8 text-center text-gray-400">Tidak ada data.</td></tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}""",

    "tax.html": """{% extends "base.html" %}
{% block content %}
<div x-data="{ show: false }" x-init="setTimeout(() => show = true, 100)">
    <div x-show="show" x-transition.opacity.duration.800ms class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden transform transition-all">
        <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-gray-50 to-white">
            <h3 class="text-lg font-bold text-gray-800"><i class="fa-solid fa-file-invoice-dollar text-red-500 mr-2"></i> Arsip Pajak Kendaraan</h3>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-gray-50/50 text-gray-500 text-xs uppercase tracking-wider">
                        <th class="p-4 font-medium">Tanggal Bayar</th>
                        <th class="p-4 font-medium">Keterangan Pajak</th>
                        <th class="p-4 font-medium">Total (Rp)</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 text-sm">
                    {% if logs %}
                        {% for log in logs %}
                        <tr class="hover:bg-red-50/50 transition-colors group">
                            <td class="p-4 text-gray-600">{{ log.date }}</td>
                            <td class="p-4 text-gray-600 capitalize">{{ log.description }}</td>
                            <td class="p-4 font-bold text-gray-800 group-hover:text-red-600 transition-colors">Rp {{ "{:,}".format(log.cost) }}</td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr><td colspan="3" class="p-8 text-center text-gray-400">Tidak ada data pajak.</td></tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}"""
}

for filename, content in html_files.items():
    with open(f"templates/{filename}", "w", encoding="utf-8") as f:
        f.write(content)
