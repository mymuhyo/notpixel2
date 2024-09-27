import os
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded, RPCError
from pyrogram.types import Message
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your bot token and API details
API_ID = "26955139"  # Get this from my.telegram.org
API_HASH = "147f0192ef238f2730ae6714f94072a9"  # Get this from my.telegram.org
BOT_TOKEN = "6215171761:AAFCi18N3Hcw8MmNV4o4Bs55g3fK_Tdgc5Q"  # Get this from @BotFather

# Sessiya fayllarini saqlash papkasi
SESSIONS_DIR = "sessions"

# Sessiya faylini saqlash uchun papka yaratish
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Bot klienti
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Telefon raqami so'raladi
@bot.on_message(filters.command("startsession") & filters.private)
async def start_session(client: Client, message: Message):
    await message.reply("Iltimos, telefon raqamingizni xalqaro formatda yuboring:\n\nMisol: `+998901234567`")

    @bot.on_message(filters.private & filters.text)
    async def receive_phone_number(client: Client, phone_msg: Message):
        phone_number = phone_msg.text.strip()

        # Telefon raqami orqali sessiya yaratish
        user_id = phone_msg.from_user.id
        session_file = os.path.join(SESSIONS_DIR, f"{user_id}.session")

        try:
            # Yangi Pyrogram klientini yaratish
            user_client = Client(
                name=str(user_id),
                api_id=API_ID,
                api_hash=API_HASH,
                phone_number=phone_number,
                workdir=SESSIONS_DIR,  # Sessiya fayllarini saqlash
            )

            # Foydalanuvchini telefon raqami bilan login qilish
            await user_client.connect()

            # O'zingizning telefon raqamingizni tekshirish
            sent_code = await user_client.send_code(phone_number)
            await phone_msg.reply(f"SMS yoki qo'ng'iroq orqali yuborilgan kodni kiriting.")

            # Kodni qabul qilish
            @bot.on_message(filters.private & filters.text)
            async def receive_code(client: Client, code_msg: Message):
                try:
                    code = code_msg.text.strip()

                    # Kod bilan login qilish
                    await user_client.sign_in(phone_number, code)
                    await code_msg.reply("Kod to'g'ri, agar sizda ikki faktorli autentifikatsiya paroli bo'lsa, uni yuboring. Agar yo'q bo'lsa, `parol yo'q` deb yozing.")

                    # Ikki faktorli autentifikatsiya uchun parol so'raladi (agar kerak bo'lsa)
                    @bot.on_message(filters.private & filters.text)
                    async def receive_password(client: Client, password_msg: Message):
                        try:
                            password = password_msg.text.strip()
                            if password.lower() != "parol yo'q":
                                # Parol bilan kirish
                                await user_client.check_password(password)

                            # Muvaffaqiyatli sessiya yaratildi
                            await user_client.stop()  # Sessiyani yaratib tugatish

                            # Sessiya faylini foydalanuvchiga yuborish
                            if os.path.exists(session_file):
                                await bot.send_document(
                                    chat_id=password_msg.chat.id,
                                    document=session_file,
                                    caption="Mana sizning sessiya faylingiz. Uni Pyrogram yoki boshqa Telegram klientingizda ishlatishingiz mumkin."
                                )
                            else:
                                await password_msg.reply("Sessiya fayli yaratilmadi. Xatolik yuz berdi.")
                        except SessionPasswordNeeded:
                            await password_msg.reply("Xato! Ikki faktorli autentifikatsiya parolini noto‘g‘ri kiritdingiz.")
                        except Exception as e:
                            await password_msg.reply(f"Xatolik yuz berdi: {e}")

                except RPCError as e:
                    await code_msg.reply(f"Kodni tasdiqlashda xatolik: {e}")

        except RPCError as e:
            await phone_msg.reply(f"Telefon raqamini tasdiqlashda xatolik: {e}")

if __name__ == "__main__":
    bot.run()