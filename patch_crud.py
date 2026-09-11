with open("main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# ADD ENDPOINTS FOR DELETE AND EDIT
crud_endpoints = """
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
"""

if "@app.get(\"/delete/" not in main_code:
    # Insert before the first @app.get("/vehicles")
    parts = main_code.split('@app.get("/vehicles")')
    main_code = parts[0] + crud_endpoints + '\n@app.get("/vehicles")' + parts[1]
    
    # Also ensure datetime is imported
    if "from datetime import datetime" not in main_code:
        main_code = main_code.replace("from datetime import date", "from datetime import date, datetime")
    
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(main_code)

# MODIFY MAINTENANCE.HTML
with open("templates/maintenance.html", "r", encoding="utf-8") as f:
    maint_html = f.read()

maint_html = maint_html.replace('<th class="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider pb-4">Biaya (Rp)</th>', '<th class="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider pb-4">Biaya (Rp)</th>\n<th class="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider pb-4">Aksi</th>')

maint_row_old = """<td class="py-4 text-orange-600 font-bold">Rp {{ "{:,.1f}".format(log.cost) }}</td>"""
maint_row_new = """<td class="py-4 text-orange-600 font-bold">Rp {{ "{:,.1f}".format(log.cost) }}</td>
<td class="py-4 text-right">
    <button @click="editData = { id: {{log.id}}, date: '{{log.date}}', category: '{{log.category}}', description: '{{log.description}}', cost: {{log.cost}} }; showModal = true" class="text-blue-500 hover:text-blue-700 mr-3"><i class="fa-solid fa-pen"></i></button>
    <a href="/delete/maintenance/{{log.id}}" onclick="return confirm('Yakin ingin menghapus data ini?')" class="text-red-500 hover:text-red-700"><i class="fa-solid fa-trash"></i></a>
</td>"""
maint_html = maint_html.replace(maint_row_old, maint_row_new)

# Add Modal
maint_modal = """
<!-- Edit Modal -->
<div x-show="showModal" style="display: none;" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div x-show="showModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
        <div x-show="showModal" class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Edit Data Servis & Oli</h3>
            <form :action="'/maintenance/edit/' + editData.id" method="POST">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Tanggal</label>
                    <input type="date" name="date" x-model="editData.date" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Kategori</label>
                    <select name="category" x-model="editData.category" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                        <option value="Oli">Oli</option>
                        <option value="Servis">Servis</option>
                        <option value="Sparepart">Sparepart</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Keterangan</label>
                    <input type="text" name="description" x-model="editData.description" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                </div>
                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Biaya (Rp)</label>
                    <input type="number" name="cost" x-model="editData.cost" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                </div>
                <div class="flex justify-end gap-3">
                    <button type="button" @click="showModal = false" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">Batal</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Simpan Perubahan</button>
                </div>
            </form>
        </div>
    </div>
</div>
"""
maint_html = maint_html.replace('<div x-data="{ show: false }"', '<div x-data="{ show: false, showModal: false, editData: {} }"\n' + maint_modal)

with open("templates/maintenance.html", "w", encoding="utf-8") as f:
    f.write(maint_html)


# MODIFY FUEL.HTML
with open("templates/fuel.html", "r", encoding="utf-8") as f:
    fuel_html = f.read()

fuel_html = fuel_html.replace('<th class="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider pb-4">Odometer</th>', '<th class="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider pb-4">Odometer</th>\n<th class="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider pb-4">Aksi</th>')

fuel_row_old = """<td class="py-4 text-gray-600 font-mono">{{ log.odometer }} KM</td>"""
fuel_row_new = """<td class="py-4 text-gray-600 font-mono">{{ log.odometer }} KM</td>
<td class="py-4 text-right">
    <button @click="editData = { id: {{log.id}}, date: '{{log.date}}', fuel_type: '{{log.fuel_type}}', volume: {{log.volume_liters}}, cost: {{log.cost}}, odometer: {{log.odometer}} }; showModal = true" class="text-blue-500 hover:text-blue-700 mr-3"><i class="fa-solid fa-pen"></i></button>
    <a href="/delete/fuel/{{log.id}}" onclick="return confirm('Yakin ingin menghapus data ini?')" class="text-red-500 hover:text-red-700"><i class="fa-solid fa-trash"></i></a>
</td>"""
fuel_html = fuel_html.replace(fuel_row_old, fuel_row_new)

# Add Modal
fuel_modal = """
<!-- Edit Modal -->
<div x-show="showModal" style="display: none;" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div x-show="showModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
        <div x-show="showModal" class="inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Edit Riwayat BBM</h3>
            <form :action="'/fuel/edit/' + editData.id" method="POST">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Tanggal</label>
                    <input type="date" name="date" x-model="editData.date" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                </div>
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Jenis BBM</label>
                        <input type="text" name="fuel_type" x-model="editData.fuel_type" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Volume (Liter)</label>
                        <input type="number" step="0.1" name="volume" x-model="editData.volume" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4 mb-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Biaya (Rp)</label>
                        <input type="number" name="cost" x-model="editData.cost" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Odometer (KM)</label>
                        <input type="number" name="odometer" x-model="editData.odometer" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                    </div>
                </div>
                <div class="flex justify-end gap-3">
                    <button type="button" @click="showModal = false" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">Batal</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Simpan Perubahan</button>
                </div>
            </form>
        </div>
    </div>
</div>
"""
fuel_html = fuel_html.replace('<div x-data="{ show: false }"', '<div x-data="{ show: false, showModal: false, editData: {} }"\n' + fuel_modal)

with open("templates/fuel.html", "w", encoding="utf-8") as f:
    f.write(fuel_html)
