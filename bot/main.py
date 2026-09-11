import os
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
    
    bbm_choosing_type = State()
    bbm_typing_cost = State()
    bbm_typing_km = State()
    
    maint_typing_desc = State()
    maint_typing_cost = State()
    maint_typing_km = State()

@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Halo! Saya Bot Pencatat Kendaraan Anda yang baru dan SUPER CEPAT! ⚡\n\n"
        "Pilih menu di bawah ini untuk berinteraksi dengan Dasbor Web Anda secara real-time.",
        reply_markup=menu_keyboard
    )

# --- ALUR CATAT PENGELUARAN (WIZARD STEP-BY-STEP) ---

@dp.message(F.text == "📝 Catat Pengeluaran Baru")
async def start_catat(message: types.Message, state: FSMContext):
    await state.clear()
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
        await message.answer("1️⃣ **Pilih Kendaraan:**", reply_markup=reply_markup, parse_mode="Markdown")
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
            f"Kendaraan: **{vehicle.name.upper()}**\n\n2️⃣ **Pilih Kategori:**",
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
    
    if category == "bbm":
        keyboard = [
            [InlineKeyboardButton(text="Pertalite", callback_data="fuel_pertalite"), InlineKeyboardButton(text="Pertamax", callback_data="fuel_pertamax")],
            [InlineKeyboardButton(text="Pertamax Turbo", callback_data="fuel_turbo"), InlineKeyboardButton(text="Solar", callback_data="fuel_solar")],
            [InlineKeyboardButton(text="Shell / BP / Vivo", callback_data="fuel_shell")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await callback.message.edit_text("3️⃣ **Pilih Jenis BBM:**", reply_markup=reply_markup, parse_mode="Markdown")
        await state.set_state(RecordState.bbm_choosing_type)
    else:
        nama_kategori = "Servis & Sparepart" if category == "servis" else ("Ganti Oli" if category == "oli" else "Pajak")
        await callback.message.edit_text(
            f"3️⃣ **Apa saja yang dilakukan/diganti?**\n\n"
            f"*(Ketikkan keterangannya, contoh: Ganti kampas rem depan, V-Belt, Oli Gardan)*",
            parse_mode="Markdown"
        )
        await state.set_state(RecordState.maint_typing_desc)

# --- WIZARD BBM ---

@dp.callback_query(RecordState.bbm_choosing_type, F.data.startswith("fuel_"))
async def process_bbm_type(callback: CallbackQuery, state: FSMContext):
    jenis = callback.data.split("_")[1]
    
    fuel_map = {
        "pertalite": ("Pertalite", 10000),
        "pertamax": ("Pertamax", 12950),
        "turbo": ("Pertamax Turbo", 14400),
        "solar": ("Solar", 6800),
        "shell": ("Shell/BP/Vivo", 14500)
    }
    
    fuel_name, fuel_price = fuel_map.get(jenis, ("BBM", 10000))
    await state.update_data(fuel_name=fuel_name, fuel_price=fuel_price)
    
    await callback.message.edit_text(
        f"✅ Jenis: **{fuel_name}**\n\n4️⃣ **Berapa total biayanya (Rupiah)?**\n*(Ketik angkanya saja, misal: 35000 atau 35rb)*",
        parse_mode="Markdown"
    )
    await state.set_state(RecordState.bbm_typing_cost)

@dp.message(RecordState.bbm_typing_cost)
async def process_bbm_cost(message: types.Message, state: FSMContext):
    text = message.text.lower().replace('.', '').replace(',', '')
    match = re.search(r'(\d+)(?:\s*(ribu|rb|k))?', text)
    if not match:
        await message.answer("⚠️ Harap masukkan angka. Berapa total biayanya?")
        return
        
    val = int(match.group(1))
    if match.group(2) in ['ribu', 'rb', 'k'] or val < 1000:
        cost = val * 1000
    else:
        cost = val
        
    await state.update_data(cost=cost)
    await message.answer(
        f"✅ Biaya: **Rp {cost:,}**\n\n5️⃣ **Berapa angka Odometer (KM) saat ini?**\n*(Lihat di speedometer Anda, ketik angkanya saja, misal: 12500)*",
        parse_mode="Markdown"
    )
    await state.set_state(RecordState.bbm_typing_km)

@dp.message(RecordState.bbm_typing_km)
async def process_bbm_km(message: types.Message, state: FSMContext):
    text = message.text.lower().replace('.', '').replace(',', '')
    match = re.search(r'(\d+)', text)
    if not match:
        await message.answer("⚠️ Harap masukkan angka KM. Berapa Odometer saat ini?")
        return
        
    odometer = int(match.group(1))
    
    # Save to DB
    data = await state.get_data()
    vehicle_id = data.get('vehicle_id')
    v_name = data.get('vehicle_name').upper()
    fuel_name = data.get('fuel_name')
    fuel_price = data.get('fuel_price')
    cost = data.get('cost')
    
    volume_liters = round(cost / fuel_price, 2)
            
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
            fuel_type=fuel_name,
            volume_liters=volume_liters,
            cost=cost,
            is_full=True
        )
        db.add(new_log)
        db.commit()
    finally:
        db.close()
        
    reply_msg = (
        f"✅ **BBM {v_name} Tersimpan!**\n\n"
        f"⛽ Isi: **{volume_liters} Liter** {fuel_name}\n"
        f"💰 Biaya: **Rp {cost:,}** *(Rp {fuel_price:,}/L)*\n"
        f"📍 Odo: **{odometer:,} KM**\n"
    )
    if konsumsi_kml > 0:
        reply_msg += (
            f"\n📈 **Analisis Konsumsi:**\n"
            f"Jarak: **{jarak_tempuh:,} KM**\n"
            f"Efisiensi: **{konsumsi_kml} KM/Liter** 🚀\n"
        )
        
    await message.answer(reply_msg, parse_mode="Markdown")
    await state.clear()

# --- WIZARD MAINTENANCE ---

@dp.message(RecordState.maint_typing_desc)
async def process_maint_desc(message: types.Message, state: FSMContext):
    desc = message.text
    await state.update_data(description=desc)
    
    await message.answer(
        f"✅ Keterangan: *{desc}*\n\n4️⃣ **Berapa total biayanya (Rupiah)?**\n*(Ketik angkanya saja, misal: 150000)*",
        parse_mode="Markdown"
    )
    await state.set_state(RecordState.maint_typing_cost)

@dp.message(RecordState.maint_typing_cost)
async def process_maint_cost(message: types.Message, state: FSMContext):
    text = message.text.lower().replace('.', '').replace(',', '')
    match = re.search(r'(\d+)(?:\s*(ribu|rb|k|juta|jt))?', text)
    if not match:
        await message.answer("⚠️ Harap masukkan angka. Berapa total biayanya?")
        return
        
    val = int(match.group(1))
    multiplier = match.group(2)
    if multiplier in ['ribu', 'rb', 'k'] or (val < 1000 and multiplier is None):
        cost = val * 1000
    elif multiplier in ['juta', 'jt']:
        cost = val * 1000000
    else:
        cost = val
        
    await state.update_data(cost=cost)
    await message.answer(
        f"✅ Biaya: **Rp {cost:,}**\n\n5️⃣ **Berapa angka Odometer (KM) saat ini?**\n*(Lihat di speedometer, ketik angkanya saja)*",
        parse_mode="Markdown"
    )
    await state.set_state(RecordState.maint_typing_km)

@dp.message(RecordState.maint_typing_km)
async def process_maint_km(message: types.Message, state: FSMContext):
    text = message.text.lower().replace('.', '').replace(',', '')
    match = re.search(r'(\d+)', text)
    if not match:
        await message.answer("⚠️ Harap masukkan angka KM. Berapa Odometer saat ini?")
        return
        
    odometer = int(match.group(1))
    
    # Save to DB
    data = await state.get_data()
    vehicle_id = data.get('vehicle_id')
    v_name = data.get('vehicle_name').upper()
    category = data.get('category')
    desc = data.get('description')
    cost = data.get('cost')
            
    db = SessionLocal()
    try:
        new_log = models.MaintenanceLog(
            vehicle_id=vehicle_id,
            date=datetime.now().date(),
            category=category.capitalize(),
            description=desc.capitalize(),
            odometer=odometer,
            cost=cost
        )
        db.add(new_log)
        db.commit()
    finally:
        db.close()
        
    await message.answer(
        f"✅ **Servis {v_name} Tersimpan!**\n\n"
        f"🛠️ Kategori: **{category.capitalize()}**\n"
        f"📝 Keterangan: {desc.capitalize()}\n"
        f"💰 Biaya: **Rp {cost:,}**\n"
        f"📍 Odo: **{odometer:,} KM**\n",
        parse_mode="Markdown"
    )
    await state.clear()

# --- HANDLER MENU (NON-FSM) ---

@dp.message(F.text == "🏍️ Garasi Saya")
async def menu_garasi(message: types.Message):
    db = SessionLocal()
    try:
        vehicles = db.query(models.Vehicle).all()
        if not vehicles:
            await message.answer("Garasi Anda masih kosong. 🏍️\nSilakan 'Tambah Kendaraan' di Web.")
            return
            
        teks = "🏍️ **GARASI SAYA** 🚗\n\n"
        for v in vehicles:
            teks += f"▪️ **{v.name.upper()}** ({v.type})\n"
            teks += f"   Plat: {v.license_plate or '-'}\n\n"
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
        
        teks = "🛢️ **STATUS OLI TERAKHIR**\n\n"
        teks += f"🏍️ Kendaraan: {v_name.capitalize()}\n"
        teks += f"📅 Tanggal: {last_oli.date}\n"
        teks += f"📍 Odometer: {last_oli.odometer:,} KM\n"
        teks += f"💰 Biaya: Rp {last_oli.cost:,}\n\n"
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
            
        teks = "📊 **5 RIWAYAT BBM TERAKHIR**\n\n"
        for log in logs:
            vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == log.vehicle_id).first()
            v_name = vehicle.name if vehicle else "?"
            teks += f"📅 {log.date} | 🏍️ {v_name.capitalize()}\n"
            teks += f"⛽ {log.fuel_type.capitalize()} (Rp{log.cost:,})\n"
            teks += f"📍 KM {log.odometer:,}\n\n"
            
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
        
        teks = f"📈 **LAPORAN BULAN INI** ({current_month}/{current_year})\n\n"
        teks += f"⛽ Total BBM: Rp {fuel_cost:,}\n"
        teks += f"🛠️ Total Servis/Lainnya: Rp {maint_cost:,}\n"
        teks += "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n"
        teks += f"💰 **TOTAL PENGELUARAN: Rp {total:,}**"
        
        await message.answer(teks, parse_mode="Markdown")
    finally:
        db.close()

@dp.message(F.text == "📉 Grafik Statistik")
async def menu_grafik(message: types.Message):
    await message.answer("Grafik Interaktif Chart.js ada di Dasbor Web Anda! 📊\n👉 http://100.101.160.117:8000")

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
