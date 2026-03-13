# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8699410544:AAFEJMk36p8Qu_8A-oi9cnYOqKNiSMo0Dhc"
ADMIN_ID = 8224239269
BANK_ID = "MB"
ACCOUNT_NO = "777190521"
ACCOUNT_NAME = "Vu Kim Huong"

user_data = {}
so_du = {}

def get_so_du(user_id):
    return so_du.get(user_id, 0)

def get_noi_dung(user_id):
    return f"NAP {user_id}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ten = update.effective_user.first_name
    await update.message.reply_text(
        f"Chao mung {ten}!\n"
        f"ID Telegram cua ban: {user_id}\n"
        f"So du: {get_so_du(user_id):,}\n\n"
        f"/help - Xem cac lenh\n"
        f"/sodu - Xem so du\n"
        f"/nap - Nap tien\n"
        f"/rut - Rut tien\n"
        f"/ab - Choi xuc xac A/B"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"ID Telegram cua ban: {user_id}\n\n"
        f"Cac lenh:\n"
        f"/start - Khoi dong\n"
        f"/sodu - Xem so du\n"
        f"/nap - Nap tien\n"
        f"/rut - Rut tien\n"
        f"/ab - Choi xuc xac A/B\n\n"
        f"Cach choi /ab:\n"
        f"1. Chon A hoac B\n"
        f"2. Nhap so tien cuoc\n"
        f"3. Xem ket qua\n"
        f"   Tong 3-10 = A\n"
        f"   Tong 11-18 = B"
    )

async def sodu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"ID cua ban: {user_id}\n"
        f"So du: {get_so_du(user_id):,}"
    )

async def nap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    noi_dung = get_noi_dung(user_id)
    qr_url = (
        f"https://img.vietqr.io/image/{BANK_ID}-{ACCOUNT_NO}-compact2.png"
        f"?accountName={ACCOUNT_NAME.replace(' ', '%20')}"
        f"&addInfo={noi_dung.replace(' ', '%20')}"
    )
    await update.message.reply_photo(
        photo=qr_url,
        caption=(
            f"NAP TIEN\n\n"
            f"Ngan hang: {BANK_ID}\n"
            f"So TK: {ACCOUNT_NO}\n"
            f"Chu TK: {ACCOUNT_NAME}\n"
            f"Noi dung: {noi_dung}\n\n"
            f"Luu y: Nhap DUNG noi dung tren de duoc cong tien!"
        )
    )

async def rut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": "rut_nhap_info"}
    await update.message.reply_text(
        f"So du hien tai: {get_so_du(user_id):,}\n\n"
        f"Nhap thong tin theo cu phap:\n"
        f"Ten ngan hang - So tai khoan - So tien\n\n"
        f"Vi du: MB - 0123456789 - 100000"
    )

async def ab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": "chon_ab"}
    keyboard = [[
        InlineKeyboardButton("A (3-10)", callback_data="chon_A"),
        InlineKeyboardButton("B (11-18)", callback_data="chon_B"),
    ]]
    await update.message.reply_text(
        f"So du: {get_so_du(user_id):,}\nBan chon A hay B?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data in ["chon_A", "chon_B"]:
        lua_chon = query.data.replace("chon_", "")
        user_data[user_id] = {"step": "nhap_tien_cuoc", "lua_chon": lua_chon}
        await query.edit_message_text(
            f"Ban chon: {lua_chon}\n"
            f"So du: {get_so_du(user_id):,}\n"
            f"Nhap so tien cuoc:"
        )

async def xu_ly_tin_nhan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    step = user_data.get(user_id, {}).get("step")

    if step == "rut_nhap_info":
        try:
            parts = [x.strip() for x in text.split("-")]
            bank = parts[0]
            stk = parts[1]
            so_tien = int(parts[2])

            if so_tien <= 0:
                await update.message.reply_text("So tien phai lon hon 0!")
                return

            if so_tien > get_so_du(user_id):
                await update.message.reply_text(
                    f"So du khong du!\nSo du hien tai: {get_so_du(user_id):,}"
                )
                return

            so_du[user_id] = get_so_du(user_id) - so_tien
            user_data[user_id] = {}

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"YEU CAU RUT TIEN\n"
                    f"User ID: {user_id}\n"
                    f"Ngan hang: {bank}\n"
                    f"So TK: {stk}\n"
                    f"So tien: {so_tien:,}\n\n"
                    f"Dung lenh /duyet_{user_id}_{so_tien} de duyet"
                )
            )
            await update.message.reply_text(
                f"Yeu cau rut {so_tien:,} da gui!\n"
                f"So du con lai: {get_so_du(user_id):,}\n"
                f"Admin se xu ly som!"
            )
        except:
            await update.message.reply_text(
                "Sai cu phap! Thu lai:\n"
                "Vi du: MB - 0123456789 - 100000"
            )
        return

    if step == "nhap_tien_cuoc":
        if not text.isdigit():
            await update.message.reply_text("Vui long nhap so tien hop le!")
            return

        so_tien_cuoc = int(text)
        if so_tien_cuoc <= 0:
            await update.message.reply_text("So tien phai lon hon 0!")
            return

        if so_tien_cuoc > get_so_du(user_id):
            await update.message.reply_text(
                f"So du khong du!\nSo du hien tai: {get_so_du(user_id):,}"
            )
            return

        lua_chon = user_data[user_id]["lua_chon"]
        user_data[user_id] = {}

        msg = await update.message.reply_text("Dang tung xuc xac...")
        dice1 = await update.message.reply_dice(emoji="\U0001F3B2")
        dice2 = await update.message.reply_dice(emoji="\U0001F3B2")
        dice3 = await update.message.reply_dice(emoji="\U0001F3B2")

        d1 = dice1.dice.value
        d2 = dice2.dice.value
        d3 = dice3.dice.value
        total = d1 + d2 + d3
        ket_qua = "A" if total <= 10 else "B"

        if lua_chon == ket_qua:
            so_du[user_id] = get_so_du(user_id) + so_tien_cuoc
            thang_thua = f"THANG! +{so_tien_cuoc:,}"
        else:
            so_du[user_id] = get_so_du(user_id) - so_tien_cuoc
            thang_thua = f"THUA! -{so_tien_cuoc:,}"

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            text=(
                f"Tong: {total}\n"
                f"Ket qua: {ket_qua}\n"
                f"Ban chon: {lua_chon}\n"
                f">>> {thang_thua}\n"
                f"So du: {get_so_du(user_id):,}"
            )
        )
        return

    await update.message.reply_text(f"Ban vua noi: {text}")

async def congtien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Ban khong co quyen!")
        return
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text(
                "Cu phap: /congtien [id_tele] [so_tien]\n"
                "Vi du: /congtien 123456789 500000"
            )
            return

        uid = int(args[0])
        so_tien = int(args[1])

        if so_tien <= 0:
            await update.message.reply_text("So tien phai lon hon 0!")
            return

        so_du[uid] = get_so_du(uid) + so_tien

        await context.bot.send_message(
            chat_id=uid,
            text=(
                f"Nap tien thanh cong!\n"
                f"So tien: +{so_tien:,}\n"
                f"So du hien tai: {get_so_du(uid):,}"
            )
        )
        await update.message.reply_text(
            f"Da cong tien thanh cong!\n"
            f"User ID: {uid}\n"
            f"So tien: +{so_tien:,}\n"
            f"So du moi: {get_so_du(uid):,}"
        )
    except:
        await update.message.reply_text(
            "Loi! Cu phap: /congtien [id_tele] [so_tien]\n"
            "Vi du: /congtien 123456789 500000"
        )

async def duyet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Ban khong co quyen!")
        return
    try:
        parts = update.message.text.split("_")
        uid = int(parts[1])
        so_tien = int(parts[2])
        await context.bot.send_message(
            chat_id=uid,
            text=(
                f"Yeu cau rut {so_tien:,} da duoc duyet!\n"
                f"Tien se ve tai khoan som."
            )
        )
        await update.message.reply_text(f"Da duyet rut {so_tien:,} cho user {uid}!")
    except:
        await update.message.reply_text("Loi! Cu phap: /duyet_userid_sotien")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("sodu", sodu))
app.add_handler(CommandHandler("nap", nap))
app.add_handler(CommandHandler("rut", rut))
app.add_handler(CommandHandler("ab", ab))
app.add_handler(CommandHandler("congtien", congtien))
app.add_handler(MessageHandler(filters.Regex(r'^/duyet_'), duyet))
app.add_handler(CallbackQueryHandler(button_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, xu_ly_tin_nhan))

print("Bot dang chay...")
app.run_polling()