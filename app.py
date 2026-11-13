import asyncio
import urllib.parse
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from deep_translator import GoogleTranslator

TOKEN = "9198035110:AAFfUdYVRrmX9GBwMwqJi4FT3QFetlR7RZM"

bot = Bot(token=TOKEN)
dp = Dispatcher()
translator = GoogleTranslator(source='ru', target='en')

class GenState(StatesGroup):
    waiting_for_prompt = State()
    waiting_for_image = State()

@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎨 Генерация по тексту", callback_data="start_gen")],
            [InlineKeyboardButton(text="🖼 Изменить свою картинку", callback_data="start_edit")]
        ]
    )
    await message.answer(
        "🤖 Бот генерации и редактирования, Developer - @Miller_Hennesey",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "start_gen")
async def ask_prompt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("✍️ Введите промпт для генерации:")
    await state.set_state(GenState.waiting_for_prompt)
    await callback.answer()

@dp.callback_query(F.data == "start_edit")
async def ask_image(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📸 Отправьте картинку и напишите в описании (подписи к фото), что именно нужно изменить или сделать.")
    await state.set_state(GenState.waiting_for_image)
    await callback.answer()

@dp.message(GenState.waiting_for_prompt, F.text)
async def process_generation(message: types.Message, state: FSMContext):
    user_text = message.text.strip()
    await state.clear()
    wait_sticker = await message.answer_sticker("CAACAgIAAxkBAAEZ78pl3W6vSgABX38...")

    try:
        translated_prompt = translator.translate(user_text)
        encoded_prompt = urllib.parse.quote(translated_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

        await message.answer_photo(photo=image_url, caption=f"✨ **Запрос:** {user_text}")
        await wait_sticker.delete()
    except Exception:
        await wait_sticker.delete()
        await message.answer("⚠️ Не удалось сгенерировать изображение. Попробуйте позже.")

@dp.message(GenState.waiting_for_image, F.photo)
async def process_image_edit(message: types.Message, state: FSMContext):
    user_caption = message.caption or "enhance image"
    await state.clear()
    wait_sticker = await message.answer_sticker("CAACAgIAAxkBAAEZ78pl3W6vSgABX38...")

    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

        translated_prompt = translator.translate(user_caption)
        encoded_prompt = urllib.parse.quote(f"{translated_prompt} based on image {photo_url}")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

        await message.answer_photo(photo=image_url, caption=f"✨ **Промпт:** {user_caption}")
        await wait_sticker.delete()
    except Exception:
        await wait_sticker.delete()
        await message.answer("⚠️ Не удалось обработать картинку. Попробуйте другой запрос.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())