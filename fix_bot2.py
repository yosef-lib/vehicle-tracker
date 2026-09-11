import re

with open('bot/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the broken send_welcome function
broken_func_regex = r'@dp\.message\(Command\("start"\)\)\nasync def send_welcome\(message: types\.Message\):.*?@dp\.message\(\)'

correct_func = """@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Halo! Saya Bot Pencatat Kendaraan Anda. 🏍️🚗\\n"
        "Silakan pilih menu di bawah ini, atau ketik langsung pengeluaran Anda (contoh: 'isi vario pertamax 35rb di km 24500')!",
        reply_markup=menu_keyboard
    )

@dp.message()"""

code = re.sub(broken_func_regex, correct_func, code, flags=re.DOTALL)

with open('bot/main.py', 'w', encoding='utf-8') as f:
    f.write(code)
