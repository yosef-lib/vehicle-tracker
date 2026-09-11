import os
import json
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Ganti dengan Token Bot Telegram Anda
BOT_TOKEN = "8944264752:AAF-0L4gj-OPyq-s6qhbpw5caHvBvKMgnjU"
OLLAMA_URL = "http://localhost:11434/api/generate"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Database sederhana untuk harga BBM & Kapasitas Tangki (Bisa dipindah ke DB nanti)
FUEL_PRICES = {
    "pertalite": 10000,
    "pertamax": 12950,
    "solar": 6800,
}
VEHICLE_CAPACITY = {
    "vario": 5.5, # Liter
    "nmax": 7.1,
}

# Fungsi untuk memanggil Hermes AI (Lokal)
async def parse_text_with_ai(text: str):
    prompt = f"""
    Anda adalah asisten cerdas pencatat pengeluaran kendaraan.
    Ekstrak data berikut menjadi format JSON dari teks ini: "{text}"
    Kunci JSON:
    - category (bisa: "bbm", "oli", "sparepart", "pajak")
    - vehicle (nama kendaraan, huruf kecil semua, e.g. "vario")
    - cost (angka total biaya)
    - odometer (angka KM jika ada, null jika tidak ada)
    - detail (misal: "pertamax", "oli motul", dsb, huruf kecil)
    Hanya output JSON saja tanpa teks lain!
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(OLLAMA_URL, json={
                "model": "hermes3:8b",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            })
            if response.status_code == 200:
                return json.loads(response.json().get("response", "{}"))
        except Exception as e:
            print("Ollama Error:", e)
    return None

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⛽ Catat BBM"), KeyboardButton(text="🛠️ Catat Servis/Sparepart")],
        [KeyboardButton(text="🏍️ Garasi Saya"), KeyboardButton(text="🛢️ Status Oli")],
        [KeyboardButton(text="📊 Riwayat BBM"), KeyboardButton(text="📈 Laporan Bulanan")],
        [KeyboardButton(text="📉 Grafik Statistik"), KeyboardButton(text="ℹ️ Bantuan")]
    ],
    resize_keyboard=True,
    persistent=True
)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Halo! Saya Bot Pencatat Kendaraan Anda. 🏍️🚗
"
        "Silakan pilih menu di bawah ini, atau ketik langsung pengeluaran Anda (contoh: 'isi vario pertamax 35rb di km 24500')!",
        reply_markup=menu_keyboard
    )"
    )

@dp.message()
async def handle_message(message: types.Message):
    await message.answer("Memproses data dengan AI... 🤖")
    
    parsed_data = await parse_text_with_ai(message.text)
    if not parsed_data:
        await message.answer("Maaf, format tidak dipahami atau AI sedang offline.")
        return

    category = parsed_data.get('category')
    vehicle = parsed_data.get('vehicle', '').lower()
    cost = parsed_data.get('cost', 0)
    detail = parsed_data.get('detail', '').lower()

    # Logika Validasi Kapasitas Tangki (Anti Meluber)
    if category == "bbm" and vehicle in VEHICLE_CAPACITY:
        # Cari jenis bensin di detail
        fuel_price = 0
        for f_name, f_price in FUEL_PRICES.items():
            if f_name in detail:
                fuel_price = f_price
                break
        
        if fuel_price > 0:
            estimated_liters = cost / fuel_price
            max_capacity = VEHICLE_CAPACITY[vehicle]
            
            if estimated_liters > max_capacity:
                await message.answer(
                    f"⚠️ **Peringatan Logika!**\n"
                    f"Maaf, Anda memasukkan nilai yang salah. Anda mengisi Rp {cost:,} untuk {detail.capitalize()}.\n"
                    f"Dengan harga Rp {fuel_price:,}/liter, itu setara dengan **{estimated_liters:.1f} Liter**.\n\n"
                    f"Sedangkan kapasitas tangki standar {vehicle.capitalize()} hanya **{max_capacity} Liter**! Tangki pasti meluber 💦.\n\n"
                    f"Silakan perbaiki (Ketik: 'Revisi, harga sebenarnya...')!"
                )
                return

    # TODO: Simpan ke database SQLite
    await message.answer(f"✅ Data berhasil dicatat!\n\nKategori: {category.capitalize()}\nKendaraan: {vehicle.capitalize()}\nBiaya: Rp{cost:,}\n\n(Ketik 'Revisi' jika ada kesalahan)")

from bot.scheduler import setup_scheduler

async def start_bot():
    print("Bot Telegram berjalan...")
    # Jalankan Scheduler (Alarm Pagi & Prediksi)
    setup_scheduler(bot)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
