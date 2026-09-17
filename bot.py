# -*- coding: utf-8 -*-
"""
Telegram-бот компании 404style
Продажа сайтов под ключ + связь с клиентами.
Всё в одном файле. Для запуска на bothost.ru.
"""

import asyncio
import json
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

# ============================================================
#  ⚙️  НАСТРОЙКИ — ЗАМЕНИ НА СВОИ
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "8950618499:AAH2O21-Of8Yl2JE-2PzaN8-aKxaO4ngmK0")

# ID администраторов (узнать у @userinfobot). Можно несколько.
ADMIN_IDS = [5170461866]

COMPANY_NAME = "404style"
COMPANY_TAGLINE = "Сайты под ключ — быстро, качественно, современно"
CONTACT_TELEGRAM = "@icyyaa"
CONTACT_EMAIL = "lokotoshserafim99@mail.ru"
CONTACT_PHONE = "+7 (918) 149-18-28"

# ============================================================
#  💾  ХРАНИЛИЩЕ (JSON-файлы рядом со скриптом)
# ============================================================

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_user(user):
    users = load_json(USERS_FILE)
    uid = user.id
    if not any(u["id"] == uid for u in users):
        users.append({
            "id": uid,
            "username": user.username,
            "first_name": user.first_name,
            "joined": datetime.now().isoformat(timespec="seconds"),
        })
        save_json(USERS_FILE, users)


# ============================================================
#  🧩  СОСТОЯНИЯ FSM
# ============================================================

class OrderForm(StatesGroup):
    name = State()
    contact = State()
    project_type = State()
    description = State()
    confirm = State()


class ContactForm(StatesGroup):
    message_text = State()


# ============================================================
#  🎛  КЛАВИАТУРЫ
# ============================================================

def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Заказать сайт")],
            [KeyboardButton(text="✉️ Связаться с нами"), KeyboardButton(text="ℹ️ О нас")],
        ],
        resize_keyboard=True,
    )


def project_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Лендинг", callback_data="pt:landing")],
        [InlineKeyboardButton(text="Корпоративный сайт", callback_data="pt:corp")],
        [InlineKeyboardButton(text="Интернет-магазин", callback_data="pt:shop")],
        [InlineKeyboardButton(text="Веб-приложение / SaaS", callback_data="pt:webapp")],
        [InlineKeyboardButton(text="Другое", callback_data="pt:other")],
    ])


def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Отправить", callback_data="order:send"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="order:cancel"),
    ]])


def contacts_kb():
    tg_username = CONTACT_TELEGRAM.lstrip("@")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать менеджеру", url=f"https://t.me/{tg_username}")],
        [InlineKeyboardButton(text="✉️ Оставить заявку", callback_data="contact:form")],
    ])


# ============================================================
#  🚀  РОУТЕР И ХЕНДЛЕРЫ
# ============================================================

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    save_user(message.from_user)
    await message.answer(
        f"👋 Добро пожаловать в <b>{COMPANY_NAME}</b>!\n\n"
        f"{COMPANY_TAGLINE}\n\n"
        "Мы делаем сайты под ключ: от идеи и дизайна до запуска и поддержки.\n\n"
        "Выберите действие в меню ниже 👇",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start — главное меню\n"
        "/help — помощь\n"
        "/cancel — отменить текущее действие",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("cancel"))
@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu_kb())


# ---------- О нас ----------

@router.message(F.text == "ℹ️ О нас")
async def about(message: Message):
    await message.answer(
        f"🏢 <b>{COMPANY_NAME}</b>\n\n"
        "Мы — команда разработчиков, дизайнеров и маркетологов. "
        "Создаём сайты, которые продают.\n\n"
        "📅 На рынке с 2025 года\n"
        "✅ Работаем под ключ\n"
        "✅ Фиксированная стоимость и сроки\n"
        "✅ Гарантия и поддержка после запуска\n"
        "✅ Современный дизайн и адаптив под мобильные\n\n"
        f"💬 Telegram: {CONTACT_TELEGRAM}\n"
        f"✉️ Email: {CONTACT_EMAIL}\n"
        f"📞 Телефон: {CONTACT_PHONE}",
        reply_markup=main_menu_kb(),
    )


# ---------- Связаться ----------

@router.message(F.text == "✉️ Связаться с нами")
async def contact(message: Message):
    await message.answer(
        "✉️ <b>Свяжитесь с нами удобным способом</b>\n\n"
        f"💬 Telegram: {CONTACT_TELEGRAM}\n"
        f"✉️ Email: {CONTACT_EMAIL}\n"
        f"📞 Телефон: {CONTACT_PHONE}\n\n"
        "Или оставьте заявку прямо здесь — ответим в течение 15 минут.",
        reply_markup=contacts_kb(),
    )


@router.callback_query(F.data == "contact:form")
async def contact_form_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Напишите ваше сообщение — мы передадим его менеджеру:")
    await state.set_state(ContactForm.message_text)
    await cb.answer()


@router.message(ContactForm.message_text)
async def contact_form_send(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    text_for_admin = (
        "📨 <b>Новое сообщение из бота</b>\n\n"
        f"👤 {user.full_name} (@{user.username or 'нет'})\n"
        f"🆔 <code>{user.id}</code>\n\n"
        f"💬 {message.text}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, text_for_admin)
        except Exception:
            pass
    await message.answer(
        "✅ Сообщение отправлено! Мы свяжемся с вами в ближайшее время.",
        reply_markup=main_menu_kb(),
    )


# ---------- Заказать сайт ----------

@router.message(F.text == "🌐 Заказать сайт")
async def order_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отлично! Давайте соберём информацию о проекте.\n\n"
        "Шаг 1/4. <b>Как вас зовут?</b>",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(OrderForm.name)


@router.message(OrderForm.name)
async def order_name(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Пожалуйста, введите имя (минимум 2 символа).")
        return
    await state.update_data(name=message.text.strip())
    await message.answer("Шаг 2/4. <b>Как с вами связаться?</b> (Telegram, телефон или email)")
    await state.set_state(OrderForm.contact)


@router.message(OrderForm.contact)
async def order_contact(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("Пожалуйста, укажите корректный контакт.")
        return
    await state.update_data(contact=message.text.strip())
    await message.answer(
        "Шаг 3/4. <b>Какой тип проекта вам нужен?</b>",
        reply_markup=project_type_kb(),
    )
    await state.set_state(OrderForm.project_type)


@router.callback_query(OrderForm.project_type, F.data.startswith("pt:"))
async def order_type(cb: CallbackQuery, state: FSMContext):
    types = {
        "pt:landing": "Лендинг",
        "pt:corp": "Корпоративный сайт",
        "pt:shop": "Интернет-магазин",
        "pt:webapp": "Веб-приложение / SaaS",
        "pt:other": "Другое",
    }
    await state.update_data(project_type=types.get(cb.data, "Другое"))
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await cb.message.answer("Шаг 4/4. <b>Опишите проект подробнее</b> (задачи, сроки, пожелания):")
    await state.set_state(OrderForm.description)
    await cb.answer()


@router.message(OrderForm.description)
async def order_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    data = await state.get_data()
    summary = (
        "📋 <b>Проверьте заявку:</b>\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Контакт: {data['contact']}\n"
        f"🌐 Тип проекта: {data['project_type']}\n"
        f"📝 Описание: {data['description']}"
    )
    await message.answer(summary, reply_markup=confirm_kb())
    await state.set_state(OrderForm.confirm)


@router.callback_query(OrderForm.confirm, F.data == "order:send")
async def order_send(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = cb.from_user
    order = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        **data,
    }
    orders = load_json(ORDERS_FILE)
    orders.append(order)
    save_json(ORDERS_FILE, orders)

    admin_text = (
        "🆕 <b>НОВАЯ ЗАЯВКА НА САЙТ</b>\n\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📞 Контакт: {data.get('contact')}\n"
        f"🌐 Тип: {data.get('project_type')}\n"
        f"📝 Описание: {data.get('description')}\n\n"
        f"🆔 Клиент: <code>{user.id}</code> (@{user.username or 'нет'})"
    )
    for admin_id in ADMIN_IDS:
        try:
            await cb.bot.send_message(admin_id, admin_text)
        except Exception:
            pass

    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await cb.message.answer(
        "✅ <b>Заявка отправлена!</b>\n\n"
        "Наш менеджер свяжется с вами в течение 15 минут. Спасибо за доверие! 🚀",
        reply_markup=main_menu_kb(),
    )
    await state.clear()
    await cb.answer("Заявка отправлена")


@router.callback_query(OrderForm.confirm, F.data == "order:cancel")
async def order_cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await cb.message.answer("Заявка отменена.", reply_markup=main_menu_kb())
    await cb.answer()


# ---------- Фолбэк ----------

@router.message()
async def fallback(message: Message):
    await message.answer(
        "Я не понял сообщение 🤔\n\n"
        "Воспользуйтесь меню ниже или командой /help.",
        reply_markup=main_menu_kb(),
    )


# ============================================================
#  ▶️  ЗАПУСК
# ============================================================

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    print("Бот 404style запущен ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")
