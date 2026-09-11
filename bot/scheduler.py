from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal
import datetime

async def morning_reminder(bot: Bot):
    """Fungsi yang akan dijalankan tiap jam 07:00 pagi"""
    # Ambil semua user dari database (biasanya kita iterasi dari DB)
    db: Session = SessionLocal()
    users = db.query(models.User).filter(models.User.telegram_id.isnot(None)).all()
    
    # Jika belum ada user di DB, kita kirim ke telegram ID admin secara manual
    # (Untuk testing, jika telegram_id tidak ada, tidak akan error).
    
    message_text = (
        "🌅 **Selamat Pagi!**\n\n"
        "Saatnya update kondisi kendaraan Anda hari ini.\n"
        "Silakan ketik atau pilih kategori pengeluaran/indikator:\n\n"
        "🔹 *Isi BBM*\n"
        "🔹 *Ganti Oli*\n"
        "🔹 *Update KM Harian*\n\n"
        "Semoga perjalanan Anda hari ini aman! 🏍️🚗"
    )

    for user in users:
        try:
            # Inline keyboard sederhana bisa ditambahkan di sini
            await bot.send_message(chat_id=user.telegram_id, text=message_text, parse_mode="Markdown")
        except Exception as e:
            print(f"Gagal mengirim ke {user.telegram_id}: {e}")
            
    db.close()

async def predict_maintenance(bot: Bot):
    """Menghitung prediksi ganti oli berdasarkan rata-rata KM Harian"""
    # Logika rumit akan berjalan di sini:
    # 1. Cek log servis oli terakhir (KM terakhir)
    # 2. Cek selisih KM harian saat ini
    # 3. Prediksi kapan menyentuh +2000 KM
    print("Menjalankan AI Prediksi Maintenance...")
    pass

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    
    # Jadwalkan alarm setiap jam 07:00 pagi (Waktu Server VPS)
    scheduler.add_job(morning_reminder, 'cron', hour=7, minute=0, args=[bot])
    
    # Jadwalkan prediksi maintenance setiap jam 07:30
    scheduler.add_job(predict_maintenance, 'cron', hour=7, minute=30, args=[bot])
    
    scheduler.start()
    print("Scheduler Alarm Pagi & Prediksi aktif!")
