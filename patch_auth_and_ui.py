import os
import re

# 1. UPDATE MAIN.PY UNTUK MENAMBAHKAN LOGIN (BASIC AUTH)
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

auth_imports = """
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
"""

# Insert auth functions after imports
if "HTTPBasic" not in main_code:
    main_code = main_code.replace("from fastapi.responses import HTMLResponse, FileResponse", "from fastapi.responses import HTMLResponse, FileResponse\n" + auth_imports)

# Inject dependency into all routes
routes = [
    ('async def read_root(request: Request, db: Session = Depends(get_db)):', 'async def read_root(request: Request, db: Session = Depends(get_db), username: str = Depends(get_current_user)):'),
    ('async def vehicles_page(request: Request):', 'async def vehicles_page(request: Request, username: str = Depends(get_current_user)):'),
    ('async def fuel_page(request: Request):', 'async def fuel_page(request: Request, username: str = Depends(get_current_user)):'),
    ('async def maintenance_page(request: Request):', 'async def maintenance_page(request: Request, username: str = Depends(get_current_user)):'),
    ('async def tax_page(request: Request):', 'async def tax_page(request: Request, username: str = Depends(get_current_user)):'),
    ('async def export_data(db: Session = Depends(get_db)):', 'async def export_data(db: Session = Depends(get_db), username: str = Depends(get_current_user)):')
]

for old, new in routes:
    main_code = main_code.replace(old, new)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)


# 2. UPDATE BASE.HTML MENJADI UI MODERN (SIDEBAR DASHBOARD)
base_html = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Tracker Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
    </style>
</head>
<body class="flex h-screen overflow-hidden text-gray-800">

    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col hidden md:flex">
        <div class="h-16 flex items-center justify-center border-b border-slate-800">
            <h1 class="text-xl font-bold text-blue-400"><i class="fa-solid fa-motorcycle mr-2"></i>Garage Analytics</h1>
        </div>
        <nav class="flex-1 px-4 py-6 space-y-2">
            <a href="/" class="flex items-center gap-3 px-4 py-3 rounded-lg bg-blue-600 text-white shadow-md hover:bg-blue-500 transition">
                <i class="fa-solid fa-chart-pie"></i> Dashboard
            </a>
            <a href="/vehicles" class="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800 transition">
                <i class="fa-solid fa-car"></i> Data Kendaraan
            </a>
            <a href="/fuel" class="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800 transition">
                <i class="fa-solid fa-gas-pump"></i> Riwayat BBM
            </a>
            <a href="/maintenance" class="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800 transition">
                <i class="fa-solid fa-wrench"></i> Servis & Oli
            </a>
            <a href="/tax" class="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800 transition">
                <i class="fa-solid fa-file-invoice-dollar"></i> Pajak
            </a>
        </nav>
        <div class="p-4 border-t border-slate-800">
            <a href="/export" class="flex items-center justify-center gap-2 w-full py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium transition shadow-lg">
                <i class="fa-solid fa-file-excel"></i> Export Excel
            </a>
        </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-y-auto">
        <!-- Topbar -->
        <header class="h-16 bg-white shadow-sm flex items-center justify-between px-6 z-10">
            <div class="flex items-center gap-4 md:hidden">
                <button class="text-gray-500 hover:text-gray-700 focus:outline-none">
                    <i class="fa-solid fa-bars text-xl"></i>
                </button>
                <h1 class="text-xl font-bold text-blue-600">Garage Analytics</h1>
            </div>
            <div class="hidden md:flex items-center">
                <h2 class="text-xl font-semibold text-gray-800">{{ title }}</h2>
            </div>
            <div class="flex items-center gap-4">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold border border-blue-200">
                        A
                    </div>
                    <span class="text-sm font-medium text-gray-700">Admin</span>
                </div>
            </div>
        </header>

        <!-- Main Page Content -->
        <main class="flex-1 p-6">
            {% block content %}{% endblock %}
        </main>
    </div>

</body>
</html>
"""

with open("templates/base.html", "w", encoding="utf-8") as f:
    f.write(base_html)

# 3. UPDATE INDEX.HTML MENJADI LEBIH MODERN
index_html = """{% extends "base.html" %}

{% block content %}
<!-- Metric Cards -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-xl">
            <i class="fa-solid fa-wallet"></i>
        </div>
        <div>
            <p class="text-sm text-gray-500 font-medium">Total Pengeluaran</p>
            <h3 class="text-2xl font-bold text-gray-800">Rp {{ "{:,}".format(total_cost) }}</h3>
        </div>
    </div>
    
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 text-xl">
            <i class="fa-solid fa-gas-pump"></i>
        </div>
        <div>
            <p class="text-sm text-gray-500 font-medium">Efisiensi BBM (Rata-rata)</p>
            <h3 class="text-2xl font-bold text-gray-800">42 KM/L</h3>
        </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 text-xl">
            <i class="fa-solid fa-oil-can"></i>
        </div>
        <div>
            <p class="text-sm text-gray-500 font-medium">Jadwal Ganti Oli</p>
            <h3 class="text-lg font-bold text-gray-800">Tersisa 1,200 KM</h3>
        </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center text-red-600 text-xl">
            <i class="fa-solid fa-file-invoice"></i>
        </div>
        <div>
            <p class="text-sm text-gray-500 font-medium">Pajak Kendaraan</p>
            <h3 class="text-lg font-bold text-gray-800">Aman (Bulan Depan)</h3>
        </div>
    </div>
</div>

<!-- Charts Row -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 lg:col-span-2">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Tren Pengeluaran (Bulan Ini)</h3>
        <div class="relative h-64 w-full">
            <canvas id="trendChart"></canvas>
        </div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Distribusi Biaya</h3>
        <div class="relative h-64 w-full flex justify-center">
            <canvas id="doughnutChart"></canvas>
        </div>
    </div>
</div>

<!-- Recent Table -->
<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="p-6 border-b border-gray-100 flex justify-between items-center">
        <h3 class="text-lg font-bold text-gray-800">Aktivitas Terakhir dari Telegram</h3>
        <button class="text-sm text-blue-600 font-medium hover:underline">Lihat Semua</button>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                    <th class="p-4 font-medium">Tanggal</th>
                    <th class="p-4 font-medium">Kendaraan</th>
                    <th class="p-4 font-medium">BBM (Liter)</th>
                    <th class="p-4 font-medium">Biaya (Rp)</th>
                    <th class="p-4 font-medium">Odometer</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 text-sm">
                {% if recent_logs %}
                    {% for log in recent_logs %}
                    <tr class="hover:bg-gray-50 transition">
                        <td class="p-4 text-gray-600">{{ log.date }}</td>
                        <td class="p-4 font-medium text-gray-800">Vario (ID: {{ log.vehicle_id }})</td>
                        <td class="p-4 text-blue-600 font-medium">{{ log.volume_liters }} L ({{ log.fuel_type }})</td>
                        <td class="p-4 font-bold text-gray-800">Rp {{ "{:,}".format(log.cost) }}</td>
                        <td class="p-4 text-gray-500">{{ "{:,}".format(log.odometer) }} KM</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr>
                        <td colspan="5" class="p-8 text-center text-gray-400">Belum ada data bensin yang dicatat bulan ini.</td>
                    </tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>

<script>
    // Inisialisasi Chart.js Modern
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: ['Minggu 1', 'Minggu 2', 'Minggu 3', 'Minggu 4'],
            datasets: [{
                label: 'Biaya BBM (Rp)',
                data: [35000, 70000, 25000, 110000],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#3b82f6',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { borderDash: [4, 4] } },
                x: { grid: { display: false } }
            }
        }
    });

    const doughnutCtx = document.getElementById('doughnutChart').getContext('2d');
    new Chart(doughnutCtx, {
        type: 'doughnut',
        data: {
            labels: ['BBM', 'Servis', 'Pajak', 'Sparepart'],
            datasets: [{
                data: [65, 20, 10, 5],
                backgroundColor: ['#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20 } }
            }
        }
    });
</script>
{% endblock %}
"""

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
