#!/usr/bin/env python3
"""
Демонстрація роботи кнопок Marketing Bot
"""
import os
from marketing_bot.senders.email_sender import EmailMessage, send_email
from marketing_bot.senders.social_sender import SocialPost, send_social_post

def demo_email_sending():
    print("=== 📧 ДЕМОНСТРАЦІЯ ВІДПРАВКИ EMAIL ===")
    print("Кнопка 'Відправити email' працює так:")
    print()
    
    # Симуляція натискання кнопки
    msg = EmailMessage(
        subject="Ваша ексклюзивна пропозиція",
        body="Привіт! Ось ваша персональна пропозиція зі знижкою 20%.",
        to="customer@example.com"
    )
    
    print("📤 Відправляємо email...")
    send_email(msg)
    print("✅ Email оброблено!")

def demo_social_posting():
    print("\n=== 📱 ДЕМОНСТРАЦІЯ ПУБЛІКАЦІЇ ПОСТУ ===")
    print("Кнопка 'Опублікувати пост' працює так:")
    print()
    
    # Симуляція натискання кнопки
    post = SocialPost(
        platform="twitter",
        content="🔥 Нова пропозиція! Знижка 20% на всі товари. Скористайтеся вже сьогодні! #sale #offer"
    )
    
    print("📤 Публікуємо пост...")
    send_social_post(post)
    print("✅ Пост оброблено!")

def main():
    print("🤖 ДЕМОНСТРАЦІЯ РОБОТИ КНОПОК MARKETING BOT")
    print("=" * 50)
    
    # Встановлюємо dry-run режим
    os.environ["SENDER_DRY_RUN"] = "true"
    os.environ["OFFLINE_MODE"] = "true"
    
    demo_email_sending()
    demo_social_posting()
    
    print("\n" + "=" * 50)
    print("💡 ВИСНОВОК:")
    print("✅ Кнопки ПРАЦЮЮТЬ!")
    print("📝 Вони логують повідомлення в dry-run режимі")
    print("🔧 Для реальної відправки налаштуйте SMTP/SendGrid")
    print("🌐 Для соцмереж налаштуйте API або Selenium")

if __name__ == "__main__":
    main()
