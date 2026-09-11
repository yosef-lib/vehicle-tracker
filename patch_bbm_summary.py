import re

with open("bot/main.py", "r", encoding="utf-8") as f:
    code = f.read()

old_bbm_handler = r"@dp\.message\(RecordState\.typing_bbm\).*?await state\.clear\(\)"

new_bbm_handler = """@dp.message(RecordState.typing_bbm)
async def process_bbm_input(message: types.Message, state: FSMContext):
    text = message.text.lower()
    data = await state.get_data()
    vehicle_id = data.get('vehicle_id')
    v_name = data.get('vehicle_name').upper()
    
    # Ekstrak Biaya
    cost_match = re.search(r'(\\d+)(?:\\s*(ribu|rb|k))?', text)
    if not cost_match:
        await message.answer("⚠️ Format salah! Saya tidak menemukan angka biaya. Coba lagi (cth: 30000 km 12000 pertalite):")
        return
        
    cost_val = int(cost_match.group(1))
    if cost_match.group(2) in ['ribu', 'rb', 'k'] or cost_val < 1000:
        cost = cost_val * 1000
    else:
        cost = cost_val
        
    # Ekstrak KM
    km_match = re.search(r'(?:km\\s*|kilometer\\s*)(\\d+)|(\\d+)\\s*km', text)
    odometer = int(km_match.group(1) or km_match.group(2)) if km_match else 0
    
    # Ekstrak Jenis dan Harga
    fuel_price = 10000 # Default
    jenis = "Pertalite"
    
    if 'pertamax turbo' in text:
        fuel_price = 14400
        jenis = "Pertamax Turbo"
    elif 'pertamax' in text:
        fuel_price = 12950
        jenis = "Pertamax"
    elif 'solar' in text:
        fuel_price = 6800
        jenis = "Solar"
    elif 'bp' in text or 'shell' in text or 'vivo' in text:
        fuel_price = 14500
        jenis = "BP/Shell/Vivo"
    
    volume_liters = round(cost / fuel_price, 2)
            
    # Simpan ke DB & Hitung Konsumsi
    db = SessionLocal()
    try:
        last_log = db.query(models.FuelLog).filter(
            models.FuelLog.vehicle_id == vehicle_id, 
            models.FuelLog.odometer > 0
        ).order_by(models.FuelLog.date.desc(), models.FuelLog.id.desc()).first()
        
        jarak_tempuh = 0
        if last_log and odometer > last_log.odometer:
            jarak_tempuh = odometer - last_log.odometer
            
        konsumsi_kml = round(jarak_tempuh / volume_liters, 1) if volume_liters > 0 and jarak_tempuh > 0 else 0
        
        new_log = models.FuelLog(
            vehicle_id=vehicle_id,
            date=datetime.now().date(),
            odometer=odometer,
            fuel_type=jenis,
            volume_liters=volume_liters,
            cost=cost,
            is_full=True
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        print(e)
    finally:
        db.close()
        
    # Balasan Ringkasan Langsung
    reply_msg = (
        f"✅ **Tersimpan! Ringkasan BBM {v_name}**\\n\\n"
        f"⛽ Isi: **{volume_liters} Liter** {jenis}\\n"
        f"💰 Biaya: **Rp {cost:,}** *(Rp {fuel_price:,}/L)*\\n"
        f"📍 Odometer Saat Ini: **{odometer:,} KM**\\n"
    )
    
    if konsumsi_kml > 0:
        reply_msg += (
            f"\\n📈 **Analisis Konsumsi:**\\n"
            f"Jarak Ditempuh: **{jarak_tempuh:,} KM**\\n"
            f"Efisiensi BBM: **{konsumsi_kml} KM/Liter** 🚀\\n"
        )
    else:
        reply_msg += "\\n*(Isi BBM berikutnya untuk melihat analisis konsumsi KM/L)*"
        
    await message.answer(reply_msg, parse_mode="Markdown")
    await state.clear()"""

code = re.sub(old_bbm_handler, new_bbm_handler, code, flags=re.DOTALL)

with open("bot/main.py", "w", encoding="utf-8") as f:
    f.write(code)

# Now edit bot/scheduler.py to add Weekly Reminders
scheduler_code = """from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal
import datetime

async def morning_reminder(bot: Bot):
    db: Session = SessionLocal()
    users = db.query(models.User).filter(models.User.telegram_id.isnot(None)).all()
    message_text = "🌅 **Selamat Pagi!** Jangan lupa update kondisi kendaraan Anda hari ini."
    for user in users:
        try:
            await bot.send_message(chat_id=user.telegram_id, text=message_text, parse_mode="Markdown")
        except:
            pass
    db.close()

async def weekly_check_reminder(bot: Bot):
    # Mengingatkan rutin tiap akhir minggu
    db: Session = SessionLocal()
    users = db.query(models.User).filter(models.User.telegram_id.isnot(None)).all()
    
    message_text = (
        "🔔 **PENGINGAT RUTIN MINGGUAN** 🔔\\n\\n"
        "Halo! Sudah akhir pekan, saatnya meluangkan waktu 5 menit untuk kendaraan Anda:\\n"
        "1. 💧 **Cek volume & warna oli** mesin lewat dipstick/kaca intip.\\n"
        "2. 🌬️ **Cek tekanan angin ban** depan dan belakang.\\n"
        "3. 🔧 **Cek rem & lampu-lampu** kendaraan.\\n\\n"
        "Kendaraan sehat, dompet selamat! 🛡️"
    )
    for user in users:
        try:
            await bot.send_message(chat_id=user.telegram_id, text=message_text, parse_mode="Markdown")
        except:
            pass
    db.close()

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    
    # Pengingat pagi harian jam 07:00
    scheduler.add_job(morning_reminder, 'cron', hour=7, minute=0, args=[bot])
    
    # Pengingat Mingguan tiap hari Sabtu (day_of_week=5) jam 08:00
    scheduler.add_job(weekly_check_reminder, 'cron', day_of_week=5, hour=8, minute=0, args=[bot])
    
    scheduler.start()
    print("Scheduler Alarm Pagi & Pengingat Mingguan aktif!")
"""

with open("bot/scheduler.py", "w", encoding="utf-8") as f:
    f.write(scheduler_code)
