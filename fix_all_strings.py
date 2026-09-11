with open('bot/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix literal newlines in garasi
code = code.replace('        teks = "🏍️ **GARASI SAYA** 🚗\n\n"', '        teks = "🏍️ **GARASI SAYA** 🚗\\n\\n"')
code = code.replace('            teks += f"▪️ **{v.name.upper()}** ({v.type})\n"', '            teks += f"▪️ **{v.name.upper()}** ({v.type})\\n"')
code = code.replace('            teks += f"   Plat: {v.license_plate or \'-\'}\n\n"', '            teks += f"   Plat: {v.license_plate or \'-\'}\\n\\n"')

# Fix literal newlines in status oli
code = code.replace('        teks = "🛢️ **STATUS OLI TERAKHIR**\n\n"', '        teks = "🛢️ **STATUS OLI TERAKHIR**\\n\\n"')
code = code.replace('        teks += f"🏍️ Kendaraan: {v_name.capitalize()}\n"', '        teks += f"🏍️ Kendaraan: {v_name.capitalize()}\\n"')
code = code.replace('        teks += f"📅 Tanggal: {last_oli.date}\n"', '        teks += f"📅 Tanggal: {last_oli.date}\\n"')
code = code.replace('        teks += f"📍 Odometer: {last_oli.odometer:,} KM\n"', '        teks += f"📍 Odometer: {last_oli.odometer:,} KM\\n"')
code = code.replace('        teks += f"📝 Keterangan: {last_oli.description.capitalize()}\n"', '        teks += f"📝 Keterangan: {last_oli.description.capitalize()}\\n"')
code = code.replace('        teks += f"💰 Biaya: Rp {last_oli.cost:,}\n\n"', '        teks += f"💰 Biaya: Rp {last_oli.cost:,}\\n\\n"')

# Fix literal newlines in riwayat bbm
code = code.replace('        teks = "📊 **5 RIWAYAT BBM TERAKHIR**\n\n"', '        teks = "📊 **5 RIWAYAT BBM TERAKHIR**\\n\\n"')
code = code.replace('            teks += f"📅 {log.date} | 🏍️ {v_name.capitalize()}\n"', '            teks += f"📅 {log.date} | 🏍️ {v_name.capitalize()}\\n"')
code = code.replace('            teks += f"⛽ {log.volume_liters}L {log.fuel_type.capitalize()} (Rp{log.cost:,})\n"', '            teks += f"⛽ {log.volume_liters}L {log.fuel_type.capitalize()} (Rp{log.cost:,})\\n"')
code = code.replace('            teks += f"📍 KM {log.odometer:,}\n\n"', '            teks += f"📍 KM {log.odometer:,}\\n\\n"')

# Fix literal newlines in laporan bulanan
code = code.replace('        teks = f"📈 **LAPORAN BULAN INI** ({current_month}/{current_year})\n\n"', '        teks = f"📈 **LAPORAN BULAN INI** ({current_month}/{current_year})\\n\\n"')
code = code.replace('        teks += f"⛽ Total BBM: Rp {fuel_cost:,}\n"', '        teks += f"⛽ Total BBM: Rp {fuel_cost:,}\\n"')
code = code.replace('        teks += f"🛠️ Total Servis/Lainnya: Rp {maint_cost:,}\n"', '        teks += f"🛠️ Total Servis/Lainnya: Rp {maint_cost:,}\\n"')
code = code.replace('        teks += "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n"', '        teks += "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\\n"')

# Fix literal newlines in message.answer
code = code.replace('''    await message.answer(f"✅ Data berhasil dicatat & disinkronkan ke Dasbor Web! 🌐

Kategori: {category.capitalize()}
Kendaraan: {vehicle.capitalize()}
Biaya: Rp{cost:,}

(Cek Grafik Dasbor Anda!)")''', '''    await message.answer(f"✅ Data berhasil dicatat & disinkronkan ke Dasbor Web! 🌐\\n\\nKategori: {category.capitalize()}\\nKendaraan: {vehicle.capitalize()}\\nBiaya: Rp{cost:,}\\n\\n(Cek Grafik Dasbor Anda!)")''')

with open('bot/main.py', 'w', encoding='utf-8') as f:
    f.write(code)
