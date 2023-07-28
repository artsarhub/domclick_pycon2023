import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


class MortgageForm(StatesGroup):
    requesting_loan_amount = State()
    requesting_initial_payment = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Приветствую! Я бот для оформления ипотеки. Пожалуйста, введите запрашиваемую сумму кредита.")
    await MortgageForm.requesting_loan_amount.set()


@dp.message_handler(state=MortgageForm.requesting_loan_amount)
async def process_loan_amount(message: types.Message, state: FSMContext):
    try:
        loan_amount = float(message.text)
        await state.update_data(loan_amount=loan_amount)
        await MortgageForm.next()
        await message.reply("Теперь введите сумму первоначального взноса (не меньше 15% от запрашиваемой суммы).")
    except ValueError:
        await message.reply("Пожалуйста, введите сумму кредита в числовом формате.")


@dp.message_handler(state=MortgageForm.requesting_initial_payment)
async def process_initial_payment(message: types.Message, state: FSMContext):
    try:
        initial_payment = float(message.text)
        data = await state.get_data()
        loan_amount = data.get('loan_amount')
        if initial_payment >= 0.15 * loan_amount:
            await message.reply("Спасибо! Вы можете подать онлайн-заявку на ипотеку на сайте "
                                "https://domclick.ru/ipoteka/programs/onlajn-zayavka.")
            await state.finish()
        else:
            await message.reply("Сумма первоначального взноса должна быть не меньше 15% от запрашиваемой "
                                "суммы кредита. Пожалуйста, укажите бОльший первоначальный взнос.")
    except ValueError:
        await message.reply("Пожалуйста, введите сумму первоначального взноса в числовом формате.")


@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.reply("Это бот для оформления ипотеки. Просто отправьте команду /start, чтобы начать.")


if __name__ == '__main__':
    from aiogram import executor
    from aiogram.dispatcher.filters import Command

    dp.register_message_handler(cmd_start, Command("start"))
    dp.register_message_handler(cmd_help, Command("help"))

    executor.start_polling(dp, skip_updates=True)
