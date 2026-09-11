import os
import re

# 1. Update bot/main.py to include ReplyKeyboardMarkup
with open("bot/main.py", "r", encoding="utf-8") as f:
    bot_code = f.read()

replacement = """
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
        "Halo! Saya Bot Pencatat Kendaraan Anda. 🏍️🚗\\n"
        "Silakan pilih menu di bawah ini, atau ketik langsung pengeluaran Anda (contoh: 'isi vario pertamax 35rb di km 24500')!",
        reply_markup=menu_keyboard
    )
"""

bot_code = re.sub(
    r'@dp\.message\(Command\("start"\)\)\nasync def send_welcome\(message: types\.Message\):\n\s+await message\.answer\(\n\s+"Halo!.*?\)!',
    replacement.strip(),
    bot_code,
    flags=re.DOTALL
)

with open("bot/main.py", "w", encoding="utf-8") as f:
    f.write(bot_code)


# 2. Add Chart.js to templates/index.html
with open("templates/index.html", "r", encoding="utf-8") as f:
    index_html = f.read()

if "chart.js" not in index_html:
    index_html = index_html.replace(
        """</main>""",
        """
    <!-- Grafik Statistik -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 mt-8">
        <div class="bg-white p-6 rounded-lg shadow-sm border">
            <h3 class="text-lg font-medium text-gray-800 mb-4">Tren Pengeluaran BBM (Minggu Ini)</h3>
            <canvas id="fuelChart" height="200"></canvas>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-sm border">
            <h3 class="text-lg font-medium text-gray-800 mb-4">Rasio Pengeluaran (BBM vs Servis)</h3>
            <canvas id="ratioChart" height="200"></canvas>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const fuelCtx = document.getElementById('fuelChart').getContext('2d');
        new Chart(fuelCtx, {
            type: 'line',
            data: {
                labels: ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'],
                datasets: [{
                    label: 'Biaya BBM (Rp)',
                    data: [15000, 0, 35000, 0, 0, 100000, 0],
                    borderColor: '#3b82f6',
                    tension: 0.3,
                    fill: true,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)'
                }]
            }
        });

        const ratioCtx = document.getElementById('ratioChart').getContext('2d');
        new Chart(ratioCtx, {
            type: 'doughnut',
            data: {
                labels: ['BBM', 'Servis', 'Pajak'],
                datasets: [{
                    data: [75, 20, 5],
                    backgroundColor: ['#3b82f6', '#f59e0b', '#ef4444']
                }]
            }
        });
    </script>
</main>
"""
    )
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)


# 3. Create missing HTML files
html_template = """
{% extends "base.html" %}

{% block content %}
<div class="bg-white p-6 rounded-lg shadow-sm border">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">{{ title }}</h2>
    <p class="text-gray-500 mb-6">Halaman ini sedang dalam pengembangan antarmuka (UI). Fitur CRUD akan segera terhubung ke database.</p>
    
    <div class="flex justify-end mb-4">
        <button class="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700">+ Tambah Data Baru</button>
    </div>
    
    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-100 text-gray-600 text-sm">
                    <th class="p-3 border-b">ID</th>
                    <th class="p-3 border-b">Data</th>
                    <th class="p-3 border-b">Status</th>
                    <th class="p-3 border-b">Aksi</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="4" class="p-8 text-center text-gray-400 italic">Data belum tersedia (Tarik dari Bot)</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

for page in ["vehicles.html", "fuel.html", "maintenance.html", "tax.html"]:
    with open(f"templates/{page}", "w", encoding="utf-8") as f:
        f.write(html_template)
