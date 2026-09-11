import re

# 1. ADD ENDPOINT TO MAIN.PY
with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

new_endpoint = """
from fastapi import Form
from fastapi.responses import RedirectResponse

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
"""

if "/vehicles/add" not in main_code:
    main_code = main_code.replace("from fastapi import FastAPI, Request, Depends", "from fastapi import FastAPI, Request, Depends, Form\nfrom fastapi.responses import RedirectResponse")
    main_code = main_code.replace("@app.get(\"/vehicles\"", new_endpoint.replace("from fastapi import Form\nfrom fastapi.responses import RedirectResponse\n", ""))

with open("main.py", "w", encoding="utf-8") as f:
    f.write(main_code)

# 2. ADD MODAL TO VEHICLES.HTML
with open("templates/vehicles.html", "r", encoding="utf-8") as f:
    html_code = f.read()

new_html = """{% extends "base.html" %}
{% block content %}
<div x-data="{ show: false, isModalOpen: false }" x-init="setTimeout(() => show = true, 100)">
    
    <!-- Header & Button -->
    <div x-show="show" x-transition.opacity.duration.800ms class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">Daftar Kendaraan</h2>
        <button @click="isModalOpen = true" class="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg font-medium shadow-lg shadow-blue-500/30 transform hover:scale-105 transition-all duration-300">
            <i class="fa-solid fa-plus mr-2"></i> Tambah Kendaraan
        </button>
    </div>

    <!-- Modal Form -->
    <div x-show="isModalOpen" style="display: none;" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <!-- Background overlay -->
            <div x-show="isModalOpen" x-transition.opacity class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
            <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            
            <!-- Modal panel -->
            <div x-show="isModalOpen" x-transition.scale.origin.bottom class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                <form action="/vehicles/add" method="POST">
                    <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                        <div class="sm:flex sm:items-start">
                            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                                <h3 class="text-lg leading-6 font-bold text-gray-900 mb-4" id="modal-title">Tambah Kendaraan Baru</h3>
                                
                                <div class="mb-4">
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Nama/Merek Kendaraan</label>
                                    <input type="text" name="name" required placeholder="Contoh: Vario 150" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                                </div>
                                <div class="mb-4">
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Jenis</label>
                                    <select name="type" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                                        <option value="Motor">Motor</option>
                                        <option value="Mobil">Mobil</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Plat Nomor (Opsional)</label>
                                    <input type="text" name="license_plate" placeholder="B 1234 XYZ" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                        <button type="submit" class="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm">Simpan</button>
                        <button type="button" @click="isModalOpen = false" class="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">Batal</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Grid Data -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% if vehicles %}
            {% for v in vehicles %}
            <div x-show="show" x-transition.opacity.duration.1000ms.delay.{{ loop.index0 * 100 }}ms class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                <div class="flex justify-between items-start mb-4">
                    <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/40">
                        <i class="fa-solid {% if v.type == 'Mobil' %}fa-car{% else %}fa-motorcycle{% endif %} text-2xl"></i>
                    </div>
                    <span class="px-3 py-1 bg-emerald-100 text-emerald-600 rounded-full text-xs font-bold tracking-wide">Aktif</span>
                </div>
                <h3 class="text-xl font-bold text-gray-800 mb-1 capitalize">{{ v.name }}</h3>
                <p class="text-gray-500 text-sm mb-1"><i class="fa-regular fa-id-card mr-1"></i> Plat: {{ v.license_plate or '-' }}</p>
                <p class="text-gray-500 text-sm mb-4"><i class="fa-solid fa-tag mr-1"></i> Jenis: {{ v.type }}</p>
                
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
                <p class="text-gray-500 max-w-sm">Silakan klik tombol "Tambah Kendaraan" di atas, atau otomatis terdaftar saat Anda mencatat pengeluaran di Telegram!</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

with open("templates/vehicles.html", "w", encoding="utf-8") as f:
    f.write(new_html)
