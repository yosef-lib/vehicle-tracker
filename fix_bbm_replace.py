with open("bot/main.py", "r", encoding="utf-8") as f:
    code = f.read()

start_marker = "@dp.message(RecordState.typing_bbm)"
end_marker = "    await state.clear()"

if start_marker in code and end_marker in code:
    start_idx = code.find(start_marker)
    end_idx = code.find(end_marker, start_idx) + len(end_marker)
    
    new_bbm_handler = """@dp.message(RecordState.typing_bbm)
async def process_bbm_input(message: types.Message, state: FSMContext):
    text = message.text.lower()
    data = await state.get_data()
    vehicle_id = data.get('vehicle_id')
    v_name = data.get('vehicle_name').upper()
    
    import re
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
        f"📍 Odo Saat Ini: **{odometer:,} KM**\\n"
    )
    
    if konsumsi_kml > 0:
        reply_msg += (
            f"\\n📈 **Analisis Konsumsi:**\\n"
            f"Jarak Ditempuh: **{jarak_tempuh:,} KM**\\n"
            f"Efisiensi BBM: **{konsumsi_kml} KM/Liter** 🚀\\n"
        )
    else:
        reply_msg += "\\n*(Isi BBM berikutnya untuk melihat efisiensi KM/L)*"
        
    await message.answer(reply_msg, parse_mode="Markdown")
    await state.clear()"""
    
    new_code = code[:start_idx] + new_bbm_handler + code[end_idx:]
    with open("bot/main.py", "w", encoding="utf-8") as f:
        f.write(new_code)
