import os
import re

with open("bot/main.py", "r", encoding="utf-8") as f:
    code = f.read()

db_imports = """
from app.database import SessionLocal, engine
from app import models
from datetime import datetime

# Pastikan tabel dibuat
models.Base.metadata.create_all(bind=engine)
"""

if "from app.database" not in code:
    code = code.replace("from aiogram.types import ReplyKeyboardMarkup, KeyboardButton", "from aiogram.types import ReplyKeyboardMarkup, KeyboardButton\n" + db_imports)

# Add odometer extraction
if "odometer =" not in code:
    code = code.replace("cost = parsed_data.get('cost', 0)", "cost = parsed_data.get('cost', 0)\n    odometer = parsed_data.get('odometer', 0)")

db_logic = """
    # --- SIMPAN KE DATABASE SQLITE ---
    db = SessionLocal()
    try:
        # Cari atau buat kendaraan (jika belum ada di database)
        db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.name == vehicle).first()
        if not db_vehicle:
            db_vehicle = models.Vehicle(name=vehicle)
            db.add(db_vehicle)
            db.commit()
            db.refresh(db_vehicle)
            
        today = datetime.now().date()
        
        if category == "bbm":
            volume = 0
            # Pastikan variabel fuel_price ada (bisa saja belum didefinisikan jika tangki tidak dicek)
            f_price = 0
            for f_name, p in FUEL_PRICES.items():
                if f_name in detail:
                    f_price = p
                    break
            
            if f_price > 0:
                volume = round(cost / f_price, 2)
                
            new_log = models.FuelLog(
                vehicle_id=db_vehicle.id,
                date=today,
                odometer=int(odometer) if odometer else 0,
                fuel_type=detail,
                volume_liters=volume,
                cost=cost,
                is_full=True
            )
            db.add(new_log)
        else:
            new_log = models.MaintenanceLog(
                vehicle_id=db_vehicle.id,
                date=today,
                category=category.capitalize(),
                description=detail,
                odometer=int(odometer) if odometer else 0,
                cost=cost
            )
            db.add(new_log)
            
        db.commit()
    except Exception as e:
        print("DB Error:", e)
    finally:
        db.close()
        
    await message.answer(f"✅ Data berhasil dicatat & disinkronkan ke Dasbor Web! 🌐\\n\\nKategori: {category.capitalize()}\\nKendaraan: {vehicle.capitalize()}\\nBiaya: Rp{cost:,}\\n\\n(Cek Grafik Dasbor Anda!)")
"""

# Replace the TODO block
code = re.sub(
    r'\s*# TODO: Simpan ke database SQLite.*?await message\.answer\(f"✅ Data berhasil dicatat!.*?\"\)',
    db_logic,
    code,
    flags=re.DOTALL
)

with open("bot/main.py", "w", encoding="utf-8") as f:
    f.write(code)
