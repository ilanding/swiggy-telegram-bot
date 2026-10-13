import asyncio
import csv
import io
import os
import re
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

PHONE_HEADERS = {
    "mobile", "mobile_number", "phone", "phone_number",
    "mobile number", "phone number", "number", "contact"
}

def normalize_phone(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"[^\d+]", "", value)
    if value.startswith("+91"):
        value = value[3:]
    elif value.startswith("91") and len(value) == 12:
        value = value[2:]
    return value

async def check_with_authorized_api(mobile: str) -> str:
    # Add an official/authorized status-check API here.
    # This bot does not automate private login endpoints or bypass WAF protections.
    return "API_NOT_CONFIGURED"

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "CSV Mobile Processor ready ✅\n\n"
        "CSV file upload karo. Header mein mobile/phone/number jaisa column name rakho; "
        "ya mobile numbers first column mein rakho.\n"
        "Abhi authorized status-check API configured nahi hai, isliye actual registration "
        "status check nahi hoga."
    )

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "CSV format example:\nmobile\n9876543210\n9123456789\n\n"
        "CSV upload karo. Output mein original row, normalized number, validation aur API status milega."
    )

@dp.message(F.document)
async def handle_csv(message: Message):
    doc = message.document
    if not (doc.file_name or "").lower().endswith(".csv"):
        await message.answer("Please .csv file upload karo.")
        return
    if doc.file_size and doc.file_size > 10 * 1024 * 1024:
        await message.answer("CSV 10 MB se chhoti honi chahiye.")
        return

    await message.answer("CSV mil gayi. Process kar raha hoon…")
    try:
        file = await bot.get_file(doc.file_id)
        content = await bot.download_file(file.file_path)
        raw = content.read().decode("utf-8-sig", errors="replace")
        try:
            dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel

        reader = csv.DictReader(io.StringIO(raw), dialect=dialect)
        if not reader.fieldnames:
            await message.answer("CSV mein header row nahi mili.")
            return

        headers = reader.fieldnames
        normalized_headers = {h.strip().lower(): h for h in headers if h}
        mobile_header = next(
            (normalized_headers[h] for h in PHONE_HEADERS if h in normalized_headers),
            None
        )
        if mobile_header is None:
            mobile_header = headers[0]
            await message.answer(f"Mobile column identify nahi hua; first column '{mobile_header}' use kar raha hoon.")

        output = io.StringIO(newline="")
        fieldnames = list(headers) + ["normalized_mobile", "validation", "status"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        count = 0

        for row in reader:
            count += 1
            mobile = normalize_phone(str(row.get(mobile_header, "")))
            valid = bool(re.fullmatch(r"[6-9]\d{9}", mobile))
            status = await check_with_authorized_api(mobile) if valid else "INVALID_NUMBER"
            result_row = dict(row)
            result_row["normalized_mobile"] = mobile
            result_row["validation"] = "VALID" if valid else "INVALID"
            result_row["status"] = status
            writer.writerow(result_row)

        if count == 0:
            await message.answer("CSV mein data rows nahi hain.")
            return

        result_file = BufferedInputFile(output.getvalue().encode("utf-8-sig"), filename="csv_results.csv")
        await message.answer_document(
            result_file,
            caption=f"Done ✅ Total rows: {count}\nStatus API_NOT_CONFIGURED hai jab tak official/authorized API connect nahi hoti."
        )
    except Exception:
        logging.exception("CSV processing failed")
        await message.answer("CSV process nahi ho paayi. File format check karke dobara try karo.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
