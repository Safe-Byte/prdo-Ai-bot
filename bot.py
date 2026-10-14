import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from google import genai

# API key-ga waxaa laga akhrinayaa deegaanka kombiyuutarka.
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY lama helin. "
        "Fadlan marka hore diyaari API key-ga."
    )

client = genai.Client(api_key=api_key)

# Xusuusta wada sheekaysiga isticmaalayaasha.
user_memory = {}


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Salaan! 👋 Waxaan ahay Prdo AI.\n\n"
        "Waxaan ku caawin karaa Af-Soomaali iyo Ingiriisi.\n"
        "Su'aashaada ii soo dir! 🤖"
    )


async def reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_memory:
        user_memory[user_id] = []

    history = user_memory[user_id]

    history.append({
        "role": "user",
        "parts": [{"text": user_text}],
    })

    try:
        response = await client.aio.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=history,
            config={
                "system_instruction": (
                    "You are Prdo AI, a helpful assistant. "
                    "Understand and answer in Somali or English "
                    "according to the user's language. "
                    "Be clear, respectful, and accurate."
                )
            },
        )

        answer = response.text or (
            "Waan ka xumahay, jawaab ma helin. "
            "Fadlan mar kale isku day."
        )

        history.append({
            "role": "model",
            "parts": [{"text": answer}],
        })

        # Ku hay 10 fariimood oo ugu dambeeyay.
        user_memory[user_id] = history[-10:]

        await update.message.reply_text(answer)

    except Exception as error:
        print(f"Gemini error: {error}")
        await update.message.reply_text(
            "Waan ka xumahay, cilad ayaa dhacday. "
            "Fadlan wax yar kadib isku day."
        )


def main():
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not telegram_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN lama helin.")

    app = Application.builder().token(telegram_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("Prdo AI waa shaqaynayaa...")
    app.run_polling()

if __name__ == "__main__":
    main()