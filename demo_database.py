#!/usr/bin/env python3
"""
Демонстрація роботи з базою даних email адрес та кампаніями
"""
import asyncio
import os
from pathlib import Path
from marketing_bot.database.email_database import EmailDatabase
from marketing_bot.services.email_campaign_service import EmailCampaignService

def demo_database_operations():
    print("=== 📋 ДЕМОНСТРАЦІЯ БАЗИ ДАНИХ EMAIL ===")
    print()
    
    # Встановлюємо dry-run режим
    os.environ["SENDER_DRY_RUN"] = "true"
    os.environ["OFFLINE_MODE"] = "true"
    
    # Ініціалізуємо сервіси
    db = EmailDatabase()
    campaign_service = EmailCampaignService()
    
    print("1️⃣ Завантаження контактів з CSV файлу...")
    added_count = db.add_contacts_from_csv(Path("data/email_contacts_example.csv"), "champions")
    print(f"   ✅ Додано {added_count} контактів")
    
    print("\n2️⃣ Статистика по сегментах:")
    stats = db.get_contact_count_by_segment()
    for segment, count in stats.items():
        print(f"   📊 {segment}: {count} контактів")
    
    print("\n3️⃣ Список контактів:")
    contacts = db.load_contacts()
    for i, contact in enumerate(contacts[:5], 1):
        print(f"   {i}. {contact.email} ({contact.name}) - {contact.segment}")
    if len(contacts) > 5:
        print(f"   ... та ще {len(contacts) - 5} контактів")
    
    return campaign_service

async def demo_campaign_operations(campaign_service):
    print("\n=== 📧 ДЕМОНСТРАЦІЯ КАМПАНІЙ ===")
    print()
    
    print("4️⃣ Створення кампанії...")
    campaign_id = await campaign_service.create_campaign(
        name="Літня розпродаж 2024",
        subject="🔥 Ексклюзивна пропозиція - знижка 20%!",
        body="""Привіт!

Ось ваша персональна пропозиція - знижка 20% на всі товари!

Скористайтеся пропозицією вже сьогодні та натисніть на кнопку нижче.

З повагою,
Команда Marketing Bot""",
        segment="champions"
    )
    print(f"   ✅ Кампанія створена! ID: {campaign_id}")
    
    print("\n5️⃣ Відправка кампанії (dry-run)...")
    result = await campaign_service.send_campaign(
        campaign_id=campaign_id,
        max_emails=3,  # Обмежуємо для демонстрації
        dry_run=True
    )
    print(f"   �� Відправлено: {result['sent']}")
    print(f"   ✅ Успішно: {result['success']}")
    print(f"   ❌ Помилок: {result['failed']}")
    
    print("\n6️⃣ Статистика кампаній:")
    stats = campaign_service.get_campaign_stats()
    print(f"   📊 Всього кампаній: {stats['total_campaigns']}")
    print(f"   📧 Всього відправлено: {stats['total_sent']}")
    print(f"   ✅ Успішних: {stats['total_success']}")
    print(f"   📈 Успішність: {stats['success_rate']:.1f}%")

def main():
    print("🤖 ДЕМОНСТРАЦІЯ РОБОТИ З БАЗОЮ ДАНИХ EMAIL")
    print("=" * 60)
    
    # Демонстрація роботи з базою даних
    campaign_service = demo_database_operations()
    
    # Демонстрація кампаній
    asyncio.run(demo_campaign_operations(campaign_service))
    
    print("\n" + "=" * 60)
    print("💡 ВИСНОВОК:")
    print("✅ База даних працює!")
    print("✅ Контакти завантажуються з CSV")
    print("✅ Кампанії створюються та відправляються")
    print("✅ Відстеження метрик працює")
    print("🔧 Для реальної роботи налаштуйте SMTP/SendGrid")
    print("🌐 Streamlit UI дозволяє управляти всім через веб-інтерфейс")

if __name__ == "__main__":
    main()
