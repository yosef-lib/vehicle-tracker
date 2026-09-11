with open('bot/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('"Garasi Anda masih kosong. 🏍️\nKetik pengisian BBM atau klik \'Tambah Kendaraan\' di Web."', '"Garasi Anda masih kosong. 🏍️\\nKetik pengisian BBM atau klik \'Tambah Kendaraan\' di Web."')
code = code.replace('"Untuk melihat Grafik Interaktif Chart.js, silakan buka Dasbor Web Anda! 📊\n👉 http://100.101.160.117:8000"', '"Untuk melihat Grafik Interaktif Chart.js, silakan buka Dasbor Web Anda! 📊\\n👉 http://100.101.160.117:8000"')
code = code.replace('"Ketikkan saja pengeluaran Anda seperti sedang chatting biasa! AI akan mengekstraknya otomatis. 🤖\n\nContoh:\n- \'Isi bensin pertamax 50rb di vario KM 24500\'\n- \'Ganti oli motul nmax harganya 150 ribu\'\n- \'Bayar pajak tahunan mobil avanza 2 juta\'"', '"Ketikkan saja pengeluaran Anda seperti sedang chatting biasa! AI akan mengekstraknya otomatis. 🤖\\n\\nContoh:\\n- \'Isi bensin pertamax 50rb di vario KM 24500\'\\n- \'Ganti oli motul nmax harganya 150 ribu\'\\n- \'Bayar pajak tahunan mobil avanza 2 juta\'"')

with open('bot/main.py', 'w', encoding='utf-8') as f:
    f.write(code)
