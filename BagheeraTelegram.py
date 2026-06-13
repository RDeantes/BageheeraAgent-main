from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import sys
import os
import asyncio
import threading

from BagheeraBrain import procesar
from vigencias import listar_vencidos

print("BOT INICIADO")
print("HOLA JEFA COMO PUEDO AYUDARTE HOY")


# 🔑 TOKEN DEL BOT (puedes definirlo en Railway/Render como TELEGRAM_TOKEN)
TOKEN = os.getenv("TELEGRAM_TOKEN", "8614896779:AAGUawkf0Vh29uAzBHBGSirlDLhxzINRmMg")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


# =========================================================
# 🎯 RESPONDER MENSAJES
# =======================================================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_usuario = update.message.text.upper()

    print("MENSAJE RECIBIDO:", mensaje_usuario)

    # 🔴 Si presiona ESC → rompe el ciclo y reinicia
    if mensaje_usuario == "ESC":
        await update.message.reply_text("🔄 Reiniciando el proceso...")
        print("Reiniciando...")
        os.execv(sys.executable, ['python'] + sys.argv)

    resultado = procesar(mensaje_usuario)

    # 🟢 Si es PDF → lo envía
    if isinstance(resultado, str) and resultado.endswith(".pdf"):
        try:
            with open(resultado, "rb") as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f
                )

            await update.message.reply_text("📄 Contrato generado y enviado correctamente")

        except Exception as e:
            print("ERROR AL ENVIAR PDF:", e)

            # 🧠 Manejo inteligente de timeout
            if "Timed out" in str(e):
                await update.message.reply_text(
                    "📄 El contrato probablemente ya fue enviado (conexión lenta)"
                )
            else:
                await update.message.reply_text("❌ Error real al enviar el PDF")

    # 🟡 Si es texto → responde normal
    elif resultado:
        await update.message.reply_text(resultado)

    # 🔴 Si algo falló
    else:
        await update.message.reply_text("⚠️ Ocurrió un error")



# =========================================================
# 🚀 INICIAR BOT
# =========================================================
async def error_handler(update, context):
    print("❌ ERROR DETECTADO:")
    print(context.error)


async def revisar_vigencias_diarias(app):
    while True:
        try:
            vencidos = listar_vencidos()
            if vencidos and ADMIN_CHAT_ID:
                texto = "⚠️ ALERTA DE VIGENCIAS VENCIDAS\n\n" + "\n".join(
                    f"- {item['nombre']} (vigencia: {item['vigencia']})" for item in vencidos
                )
                await app.bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=texto)
        except Exception as e:
            print("ERROR EN REVISION DIARIA:", e)
        await asyncio.sleep(86400)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    # 🔥 AGREGAR HANDLER DE ERRORES
    app.add_error_handler(error_handler)

    print("Bagheera está corriendo...")

    thread = threading.Thread(
        target=lambda: asyncio.run(revisar_vigencias_diarias(app)),
        daemon=True,
        name="vigencias-diarias"
    )
    thread.start()

    app.run_polling()