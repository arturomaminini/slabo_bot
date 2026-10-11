import asyncio
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import os
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class OrderForm(StatesGroup):
    role = State()
    region = State()
    district = State()
    task_type = State()
    details = State()


def kb_role():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Клиент")
    kb.button(text="Специалист")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def kb_region():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Москва")
    kb.button(text="Московская область")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def kb_tasks():
    kb = ReplyKeyboardBuilder()
    kb.button(text="1. Автоматика для ворот")
    kb.button(text="2. Видеонаблюдение")
    kb.button(text="3. Усиление сотовой связи")
    kb.button(text="4. Система контроля доступа")
    kb.button(text="5. Домофония")
    kb.button(text="6. Интернет")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def kb_remove():
    return types.ReplyKeyboardRemove()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы клиент или специалист?", reply_markup=kb_role())
    await state.set_state(OrderForm.role)


@dp.message(OrderForm.role, F.text.in_({"Клиент", "Специалист"}))
async def choose_role(message: types.Message, state: FSMContext):
    role = message.text
    await state.update_data(role=role)

    if role == "Клиент":
        await message.answer(
            "Вы находитесь в Москве или в области?",
            reply_markup=kb_region(),
        )
        await state.set_state(OrderForm.region)
    else:
        await message.answer(
            "Раздел для специалистов в разработке. Напишите /start, чтобы начать заново.",
            reply_markup=kb_remove(),
        )
        await state.clear()


@dp.message(OrderForm.region, F.text.in_({"Москва", "Московская область"}))
async def choose_region(message: types.Message, state: FSMContext):
    region = message.text
    await state.update_data(region=region)

    if region == "Москва":
        await message.answer("Укажите район:", reply_markup=kb_remove())
    else:
        await message.answer("Укажите город или населённый пункт:", reply_markup=kb_remove())

    await state.set_state(OrderForm.district)


@dp.message(OrderForm.district, F.text)
async def enter_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer("Выберите тип задачи:", reply_markup=kb_tasks())
    await state.set_state(OrderForm.task_type)


TASKS = {
    "1. Автоматика для ворот",
    "2. Видеонаблюдение",
    "3. Усиление сотовой связи",
    "4. Система контроля доступа",
    "5. Домофония",
    "6. Интернет",
}


@dp.message(OrderForm.task_type, F.text.in_(TASKS))
async def choose_task(message: types.Message, state: FSMContext):
    await state.update_data(task_type=message.text)
    await message.answer(
        "Укажите точный адрес, номер телефона и диапазон удобных дат:",
        reply_markup=kb_remove(),
    )
    await state.set_state(OrderForm.details)


@dp.message(OrderForm.details, F.text)
async def enter_details(message: types.Message, state: FSMContext):
    data = await state.get_data()

    region_label = "Москва" if data["region"] == "Москва" else "Московская область"
    district_label = "Район" if data["region"] == "Москва" else "Город / населённый пункт"

    summary = (
        "📋 Ваша заявка:\n\n"
        f"1. Локация: {region_label}\n"
        f"2. {district_label}: {data['district']}\n"
        f"3. Тип задачи: {data['task_type']}\n"
        f"4. Адрес, телефон и даты:\n{message.text}"
    )

    await message.answer(summary)
    await message.answer("Спасибо! Заявка принята ✅\nЧтобы начать заново — /start")
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
