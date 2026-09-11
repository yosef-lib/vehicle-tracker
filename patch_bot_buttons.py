import re

with open("bot/main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace the lazy button handlers with actual database fetching logic
lazy_handlers = r'@dp\.message\(F\.text == "🏍️ Garasi Saya"\).*?@dp\.message\(F\.text == "ℹ️ Bantuan"\)\nasync def menu_bantuan\(message: types\.Message\):\n    await message\.answer\("Ketikkan saja apa yang Anda keluarkan dengan bahasa natural\. AI akan mengurus sisanya! 🤖"\)'

real_handlers = """@dp.message(F.text == "🏍️ Garasi Saya")
async def menu_garasi(message: types.Message):
    db = SessionLocal()
    try:
        vehicles = db.query(models.Vehicle).all()
        if not vehicles:
            await message.answer("Garasi Anda masih kosong. 🏍️\\nKetik pengisian BBM atau klik 'Tambah Kendaraan' di Web.")
            return
            
        teks = "🏍️ **GARASI SAYA** 🚗\\n\\n"
        for v in vehicles:
            teks += f"▪️ **{v.name.upper()}** ({v.type})\\n"
            teks += f"   Plat: {v.license_plate or '-'}\\n\\n"
        await message.answer(teks, parse_mode="Markdown")
    finally:
        db.close()

@dp.message(F.text == "🛢️ Status Oli")
async def menu_status_oli(message: types.Message):
    db = SessionLocal()
    try:
        # Ambil log ganti oli terakhir
        last_oli = db.query(models.MaintenanceLog).filter(models.MaintenanceLog.category.ilike('%oli%')).order_by(models.MaintenanceLog.date.desc()).first()
        if not last_oli:
            await message.answer("Belum ada catatan ganti oli di sistem. 🛢️")
            return
            
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == last_oli.vehicle_id).first()
        v_name = vehicle.name if vehicle else "Kendaraan"
        
        teks = "🛢️ **STATUS OLI TERAKHIR**\\n\\n"
        teks += f"🏍️ Kendaraan: {v_name.capitalize()}\\n"
        teks += f"📅 Tanggal: {last_oli.date}\\n"
        teks += f"📍 Odometer: {last_oli.odometer:,} KM\\n"
        teks += f"📝 Keterangan: {last_oli.description.capitalize()}\\n"
        teks += f"💰 Biaya: Rp {last_oli.cost:,}\\n\\n"
        teks += "*Catat terus pengeluaran Anda agar prediksi ganti oli berikutnya lebih akurat!*"
        
        await message.answer(teks, parse_mode="Markdown")
    finally:
        db.close()

@dp.message(F.text == "📊 Riwayat BBM")
async def menu_riwayat_bbm(message: types.Message):
    db = SessionLocal()
    try:
        logs = db.query(models.FuelLog).order_by(models.FuelLog.date.desc()).limit(5).all()
        if not logs:
            await message.answer("Belum ada riwayat pengisian BBM. ⛽")
            return
            
        teks = "📊 **5 RIWAYAT BBM TERAKHIR**\\n\\n"
        for log in logs:
            vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == log.vehicle_id).first()
            v_name = vehicle.name if vehicle else "?"
            teks += f"📅 {log.date} | 🏍️ {v_name.capitalize()}\\n"
            teks += f"⛽ {log.volume_liters}L {log.fuel_type.capitalize()} (Rp{log.cost:,})\\n"
            teks += f"📍 KM {log.odometer:,}\\n\\n"
            
        teks += "*(Cek Dasbor Web untuk melihat riwayat selengkapnya!)*"
        await message.answer(teks, parse_mode="Markdown")
    finally:
        db.close()

@dp.message(F.text == "📈 Laporan Bulanan")
async def menu_laporan(message: types.Message):
    db = SessionLocal()
    try:
        from sqlalchemy import extract, func
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        fuel_cost = db.query(func.sum(models.FuelLog.cost)).filter(
            extract('month', models.FuelLog.date) == current_month,
            extract('year', models.FuelLog.date) == current_year
        ).scalar() or 0
        
        maint_cost = db.query(func.sum(models.MaintenanceLog.cost)).filter(
            extract('month', models.MaintenanceLog.date) == current_month,
            extract('year', models.MaintenanceLog.date) == current_year
        ).scalar() or 0
        
        total = fuel_cost + maint_cost
        
        teks = f"📈 **LAPORAN BULAN INI** ({current_month}/{current_year})\\n\\n"
        teks += f"⛽ Total BBM: Rp {fuel_cost:,}\\n"
        teks += f"🛠️ Total Servis/Lainnya: Rp {maint_cost:,}\\n"
        teks += "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\\n"
        teks += f"💰 **TOTAL PENGELUARAN: Rp {total:,}**"
        
        await message.answer(teks, parse_mode="Markdown")
    finally:
        db.close()

@dp.message(F.text == "📉 Grafik Statistik")
async def menu_grafik(message: types.Message):
    await message.answer("Untuk melihat Grafik Interaktif Chart.js, silakan buka Dasbor Web Anda! 📊\\n👉 http://100.101.160.117:8000")

@dp.message(F.text == "ℹ️ Bantuan")
async def menu_bantuan(message: types.Message):
    await message.answer("Ketikkan saja pengeluaran Anda seperti sedang chatting biasa! AI akan mengekstraknya otomatis. 🤖\\n\\nContoh:\\n- 'Isi bensin pertamax 50rb di vario KM 24500'\\n- 'Ganti oli motul nmax harganya 150 ribu'\\n- 'Bayar pajak tahunan mobil avanza 2 juta'")"""

code = re.sub(lazy_handlers, real_handlers, code, flags=re.DOTALL)

with open("bot/main.py", "w", encoding="utf-8") as f:
    f.write(code)
