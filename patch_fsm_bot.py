import re

fsm_imports = """
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import StateFilter

class FormRecord(StatesGroup):
    choosing_vehicle = State()
    typing_bbm = State()
    typing_maintenance = State()
"""

# We'll completely rewrite bot/main.py to be robust and AI-free
full_bot_code = """import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database import SessionLocal, engine
from app import models
from datetime import datetime
import re

# Pastikan tabel dibuat
models.Base.metadata.create_all(bind=engine)

BOT_TOKEN = "8944264752:AAF-0L4gj-OPyq-s6qhbpw5caHvBvKMgnjU"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Catat Pengeluaran Baru")],
        [KeyboardButton(text="🏍️ Garasi Saya"), KeyboardButton(text="🛢️ Status Oli")],
        [KeyboardButton(text="📊 Riwayat BBM"), KeyboardButton(text="📈 Laporan Bulanan")],
        [KeyboardButton(text="📉 Grafik Statistik"), KeyboardButton(text="ℹ️ Bantuan")]
    ],
    resize_keyboard=True,
    persistent=True
)

class RecordState(StatesGroup):
    choosing_vehicle = State()
    choosing_category = State()
    typing_bbm = State()
    typing_maintenance = State()

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Halo! Saya Bot Pencatat Kendaraan Anda yang baru dan SUPER CEPAT! ⚡\\n\\n"
        "Pilih menu di bawah ini untuk berinteraksi dengan Dasbor Web Anda secara real-time.",
        reply_markup=menu_keyboard
    )

# --- ALUR CATAT PENGELUARAN (FSM) ---

@dp.message(F.text == "📝 Catat Pengeluaran Baru")
async def start_catat(message: types.Message, state: FSMContext):
    db = SessionLocal()
    try:
        vehicles = db.query(models.Vehicle).all()
        if not vehicles:
            await message.answer("Garasi Anda kosong! Silakan tambah kendaraan dulu di Dasbor Web.")
            return
            
        keyboard = []
        for v in vehicles:
            keyboard.append([InlineKeyboardButton(text=f"🏍️ {v.name.capitalize()}", callback_data=f"veh_{v.id}")])
            
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await message.answer("Pilih kendaraan mana yang ingin dicatat:", reply_markup=reply_markup)
        await state.set_state(RecordState.choosing_vehicle)
    finally:
        db.close()

@dp.callback_query(RecordState.choosing_vehicle, F.data.startswith("veh_"))
async def process_vehicle_choice(callback: CallbackQuery, state: FSMContext):
    vehicle_id = int(callback.data.split("_")[1])
    
    db = SessionLocal()
    try:
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
        await state.update_data(vehicle_id=vehicle.id, vehicle_name=vehicle.name)
        
        keyboard = [
            [InlineKeyboardButton(text="⛽ Isi BBM", callback_data="cat_bbm")],
            [InlineKeyboardButton(text="🛠️ Servis/Sparepart", callback_data="cat_servis")],
            [InlineKeyboardButton(text="🛢️ Ganti Oli", callback_data="cat_oli")],
            [InlineKeyboardButton(text="🧾 Pajak", callback_data="cat_pajak")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await callback.message.edit_text(
            f"Kendaraan terpilih: **{vehicle.name.upper()}**\\nKategori pengeluaran apa?",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        await state.set_state(RecordState.choosing_category)
    finally:
        db.close()

@dp.callback_query(RecordState.choosing_category, F.data.startswith("cat_"))
async def process_category_choice(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    
    data = await state.get_data()
    v_name = data.get('vehicle_name').upper()
    
    if category == "bbm":
        await callback.message.edit_text(
            f"⛽ **BBM untuk {v_name}**\\n\\n"
            f"Ketik biaya, Odometer (KM), dan Jenis BBM.\\n"
            f"Contoh: *30000 km 12800 pertalite*",
            parse_mode="Markdown"
        )
        await state.set_state(RecordState.typing_bbm)
    else:
        nama_kategori = "Servis/Sparepart" if category == "servis" else ("Ganti Oli" if category == "oli" else "Pajak")
        await callback.message.edit_text(
            f"🛠️ **{nama_kategori} untuk {v_name}**\\n\\n"
            f"Ketik biaya, Odometer (KM), dan Keterangan.\\n"
            f"Contoh: *150000 km 12800 ganti busi dan kampas*",
            parse_mode="Markdown"
        )
        await state.set_state(RecordState.typing_maintenance)

@dp.message(RecordState.typing_bbm)
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
    
    # Ekstrak Jenis
    jenis = "BBM"
    for j in ['pertalite', 'pertamax', 'solar', 'shell', 'bp', 'vivo']:
        if j in text:
            jenis = j.capitalize()
            break
            
    # Simpan ke DB
    db = SessionLocal()
    try:
        new_log = models.FuelLog(
            vehicle_id=vehicle_id,
            date=datetime.now().date(),
            odometer=odometer,
            fuel_type=jenis,
            volume_liters=0, # Bisa dihitung nanti
            cost=cost,
            is_full=True
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        print(e)
    finally:
        db.close()
        
    await message.answer(f"✅ Tersimpan Kilat ⚡\\n\\nKendaraan: {v_name}\\nBBM: {jenis}\\nBiaya: Rp {cost:,}\\nOdo: {odometer} KM")
    await state.clear()

@dp.message(RecordState.typing_maintenance)
async def process_maintenance_input(message: types.Message, state: FSMContext):
    text = message.text.lower()
    data = await state.get_data()
    vehicle_id = data.get('vehicle_id')
    v_name = data.get('vehicle_name').upper()
    category = data.get('category')
    
    # Ekstrak Biaya
    cost_match = re.search(r'(\\d+)(?:\\s*(ribu|rb|k|juta|jt))?', text)
    if not cost_match:
        await message.answer("⚠️ Format salah! Saya tidak menemukan angka biaya. Coba lagi:")
        return
        
    cost_val = int(cost_match.group(1))
    multiplier = cost_match.group(2)
    if multiplier in ['ribu', 'rb', 'k'] or (cost_val < 1000 and multiplier is None):
        cost = cost_val * 1000
    elif multiplier in ['juta', 'jt']:
        cost = cost_val * 1000000
    else:
        cost = cost_val
        
    # Ekstrak KM
    km_match = re.search(r'(?:km\\s*|kilometer\\s*)(\\d+)|(\\d+)\\s*km', text)
    odometer = int(km_match.group(1) or km_match.group(2)) if km_match else 0
    
    # Hapus biaya dan km dari keterangan
    keterangan = re.sub(r'\\b(\\d+)(?:\\s*(ribu|rb|k|juta|jt))?\\b', '', text)
    keterangan = re.sub(r'(?:km\\s*|kilometer\\s*)(\\d+)|(\\d+)\\s*km', '', keterangan).strip()
    if len(keterangan) < 2:
        keterangan = "Lainnya"
        
    # Simpan ke DB
    db = SessionLocal()
    try:
        new_log = models.MaintenanceLog(
            vehicle_id=vehicle_id,
            date=datetime.now().date(),
            category=category.capitalize(),
            description=keterangan.capitalize(),
            odometer=odometer,
            cost=cost
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        print(e)
    finally:
        db.close()
        
    await message.answer(f"✅ Tersimpan Kilat ⚡\\n\\nKendaraan: {v_name}\\nKategori: {category.capitalize()}\\nBiaya: Rp {cost:,}\\nKeterangan: {keterangan.capitalize()}")
    await state.clear()


# --- HANDLER MENU (NON-FSM) ---

@dp.message(F.text == "🏍️ Garasi Saya")
async def menu_garasi(message: types.Message):
    db = SessionLocal()
    try:
        vehicles = db.query(models.Vehicle).all()
        if not vehicles:
            await message.answer("Garasi Anda masih kosong. 🏍️\\nSilakan 'Tambah Kendaraan' di Web.")
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
        teks += f"💰 Biaya: Rp {last_oli.cost:,}\\n\\n"
        await message.answer(teks, parse_mode="Markdown")
    finally:
        db.close()

@dp.message(F.text == "📊 Riwayat BBM")
async def menu_riwayat_bbm(message: types.Message):
    db = SessionLocal()
    try:
        logs = db.query(models.FuelLog).order_by(models.FuelLog.date.desc()).limit(5).all()
        if not logs:
            await message.answer("Belum ada riwayat BBM. ⛽")
            return
            
        teks = "📊 **5 RIWAYAT BBM TERAKHIR**\\n\\n"
        for log in logs:
            vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == log.vehicle_id).first()
            v_name = vehicle.name if vehicle else "?"
            teks += f"📅 {log.date} | 🏍️ {v_name.capitalize()}\\n"
            teks += f"⛽ {log.fuel_type.capitalize()} (Rp{log.cost:,})\\n"
            teks += f"📍 KM {log.odometer:,}\\n\\n"
            
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
    await message.answer("Grafik Interaktif Chart.js ada di Dasbor Web Anda! 📊\\n👉 http://100.101.160.117:8000")

@dp.message(F.text == "ℹ️ Bantuan")
async def menu_bantuan(message: types.Message):
    await message.answer("Klik '📝 Catat Pengeluaran Baru', lalu ikuti tombol petunjuknya! 🚀")

@dp.message()
async def fallback(message: types.Message):
    await message.answer("Silakan gunakan tombol menu di bawah 👇")

from bot.scheduler import setup_scheduler

async def start_bot():
    print("Bot Telegram berjalan (Mode Super Cepat FSM)...")
    setup_scheduler(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
"""

with open("bot/main.py", "w", encoding="utf-8") as f:
    f.write(full_bot_code)
