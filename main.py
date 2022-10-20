import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from bot_token import token
from all_sender import *
from all_checkers import *
from keyboard_all import *
import aiohttp
import json
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import asyncio


storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot=bot, storage=storage)

logging.basicConfig(filename='bot_info.log', encoding='utf-8', level=logging.INFO)


# Машина состояний.
class ClientStatesGroup(StatesGroup):
    network_scan = State()
    balance_scan = State()

    sender_network_choice = State()  # Выбор сети для отправки
    sender_token_choice = State()  # Выбор токена для отправки
    sender_address = State()  # Адреса отправителей
    sender_private = State()  # Приватные ключи кошельков
    amount_of_token = State()  # Количество токенов
    reciever_addresses = State()  # Получаем адреса получателей токенов

    amount_of_gwei = State()  # Для сети эфира. Пользователь указывает кол-во gwei
    amount_of_gas = State()  # Для сети эфира. Пользователь указывает лимит газа


# Получаем цену токена с бинанса
async def get_price(currency1: str, currency2: str):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={currency1}{currency2}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as responce:
            price_data = await responce.text()
            logging.info(price_data)
    return json.loads(price_data)


async def msg_sender(msg, send_info):
    b = ''
    ch = len(send_info)
    for i, inf in enumerate(send_info):
        if i % 10 == 0 and i != 0:
            await bot.send_message(msg.from_user.id, b, parse_mode='HTML')
            b = ''
            ch = ch - i
        elif i % 10 != 0 and ch < 10:
            b = b + f'{inf}\n{str("<b>─</b>")*40}\n'
        else:
            b = b + f'{inf}\n{str("<b>─</b>")*40}\n'
    await bot.send_message(msg.from_user.id, b, reply_markup=check_keyboard, parse_mode='HTML')
    return True


async def gwei_price(net: str):
    provider_link = net
    web3 = Web3(Web3.HTTPProvider(provider_link))
    gwei = round(web3.fromWei(web3.eth.gas_price, 'gwei'), 0)
    return gwei


async def wait_time(info):
    sender_adds = info['sender_adds']
    sender_adds = sender_adds.split('\n')
    reciever_adds = info['reciever']
    reciever_adds = reciever_adds.split('\n')
    if len(sender_adds) == len(reciever_adds):
        delay_time = 20
    elif len(sender_adds) == 1:
        delay_time = len(reciever_adds) * 10
    elif len(reciever_adds) == 1:
        delay_time = 20

    return delay_time


# Команда старт. Выдает пользователю инструкции. Бот может начинать работу и не с нее.
@dp.message_handler(commands=['start'])
async def start_command(msg: types.Message):
    await msg.reply(f"Выберите следующее действие:\n"
                    f"1. Проверить баланс кошелька\n"
                    f"2. Узнать текущую стоимость валюты\n "
                    f"(Данные о курсах берутся с Binance)\n"
                    f"3. Отправить токен", reply_markup=check_keyboard)


# Сбрасывает машину состояний. Возможен выход из любого состояния.
@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await msg.reply('Отменил', reply_markup=check_keyboard)
    await state.finish()


# Начало раздела "Отправка токена"
@dp.message_handler(Text(equals='Отправить токен', ignore_case=True), state=None)
async def sender_start(msg: types.message):
    await ClientStatesGroup.sender_network_choice.set()
    logging.info(msg.from_user.username)
    logging.info(msg.from_user.id)
    await msg.answer('Выберите сеть: BSC, ETH',
                     reply_markup=sender_keyboard)


@dp.message_handler(state=ClientStatesGroup.sender_network_choice)
async def sender_netwok_choice(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['network'] = msg.text.lower()
    if data['network'] == 'eth':
        await ClientStatesGroup.amount_of_gwei.set()
        gwei = await gwei_price(ethereum_link)
        await bot.send_message(msg.from_user.id, f'Введите кол-во GWEI.\nТекущее кол-во GWEI в сети: '
                                                 f'<b><code>{gwei}</code></b>',
                               parse_mode='HTML', reply_markup=cancel_keyboard)
    elif data['network'] == 'bsc':
        await ClientStatesGroup.amount_of_gwei.set()
        gwei = await gwei_price(bsc_link)
        await bot.send_message(msg.from_user.id, f'Минимальный баланс $ в BNB для отправки транзакции:\n'
                                                 'Для BNB: 0.03$ (5 GWEI, 21000 GAS)\n'
                                                 'Для BUSD/USDT: 0.08$ (5 GWEI, 75000 GAS)\n'
                                                 f'Текущее значение GWEI - <b><code>{gwei}</code></b>\n',
                               parse_mode='HTML', reply_markup=cancel_keyboard)
    elif data['network'] == 'test':  # Удалить или скрыть после тестов
        await ClientStatesGroup.sender_token_choice.set()
        await bot.send_message(msg.from_user.id, 'Для отправки транзакции на вашем кошельке должно быть минимум'
                                                 ' 0.08$ в BNB.\nОдна транзакция сжигает примерно 0.03$ в BNB.\n'
                                                 'Введите название токена для отправки: "BNB", "USDT", "BUSD"',
                               reply_markup=cancel_keyboard)
    else:
        await ClientStatesGroup.sender_network_choice.set()
        await bot.send_message(msg.from_user.id, 'Введенная вами сеть не поддерживается. '
                                                 'Попытайтесь ввести название снова.')


@dp.message_handler(state=ClientStatesGroup.amount_of_gwei)
async def sender_gwei(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gwei'] = msg.text.lower()
    await ClientStatesGroup.amount_of_gas.set()
    await bot.send_message(msg.from_user.id, 'Введите количество газа для транзакции. Лишний газ не сгорит. '
                                             'Вводите с запасом. <b>Администрация за фейл транзакции '
                                             'ответственности не несет.</b>', parse_mode='html')


@dp.message_handler(state=ClientStatesGroup.amount_of_gas)
async def sender_gas(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gas'] = msg.text.lower()
    if data['network'] == 'eth':
        await ClientStatesGroup.sender_token_choice.set()
        await bot.send_message(msg.from_user.id, 'Введите название токена для отправки: \n"ETH", "USDT"')
    elif data['network'] == 'bsc':
        await ClientStatesGroup.sender_token_choice.set()
        await bot.send_message(msg.from_user.id, 'Введите название токена для отправки: \n"BNB", "USDT", "BUSD"')


@dp.message_handler(state=ClientStatesGroup.sender_token_choice)
async def sender_token_choice(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['token'] = msg.text.lower()
    if msg.text.lower() in ['bnb', 'usdt', 'busd'] and data['network'] == 'bsc' \
            or msg.text.lower() in ['usdt', 'eth'] and data['network'] == 'eth' \
            or msg.text.lower() == 'bnb' and data['network'] == 'test':
        await ClientStatesGroup.sender_address.set()
        await bot.send_message(msg.from_user.id, 'Введите адрес(а) отправителя (1 строка - один адрес)')
    else:
        await bot.send_message(msg.from_user.id, 'Название токена указано неверно. Попытайтесь еще раз.')
        await ClientStatesGroup.sender_token_choice.set()


@dp.message_handler(state=ClientStatesGroup.sender_address)
async def sender_addresses(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sender_adds'] = msg.text
    await ClientStatesGroup.sender_private.set()
    await bot.send_message(msg.from_user.id, 'Введите приватный ключ(и) отправителя (1 строка - один ключ)')


@dp.message_handler(state=ClientStatesGroup.sender_private)
async def sender_private(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sender_private'] = msg.text
    await ClientStatesGroup.amount_of_token.set()
    await bot.send_message(msg.from_user.id, 'Введите сумму для отправки на каждый адрес(Не целые числа через ".")')


@dp.message_handler(state=ClientStatesGroup.amount_of_token)
async def amount_of_token(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        amount = msg.text
        data['amount'] = amount.replace(',', '.')
    await ClientStatesGroup.reciever_addresses.set()
    await bot.send_message(msg.from_user.id, 'Введите адрес(а) получателя (1 строка - один адрес)')


@dp.message_handler(state=ClientStatesGroup.reciever_addresses)
async def reciever_addresses(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['reciever'] = msg.text
    delay_time = await wait_time(data)
    await bot.send_message(msg.from_user.id, f'Начал работу. Примерное время ожидания - {delay_time} секунд.')
    sender_info = asyncio.create_task(token_sender(data))
    hashes = await sender_info
    msg_for_send = asyncio.create_task(msg_sender(msg ,hashes))
    msg_for_send_f = await msg_for_send
    await state.finish()


# Запуск машины состояний вкладки БАЛАНС.
@dp.message_handler(Text(equals='Баланс', ignore_case=True), state=None)
async def balance_start(msg: types.Message):
    await ClientStatesGroup.network_scan.set()
    logging.info(msg.from_user.username)
    logging.info(msg.from_user.id)
    await msg.answer('Выберите сеть: \nArbitrum (ARB)\nBinance Smart Chain (BSC)\nEthereum (ETH)\nPolygon (POL)',
                     reply_markup=balance_keyboard)


# Выбор сети, в которой мы проверяем баланс.
@dp.message_handler(state=ClientStatesGroup.network_scan)
async def arb_balance_check(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['network'] = msg.text.lower()
    await ClientStatesGroup.balance_scan.set()
    await msg.answer('Введите адрес или адреса (1 строка - один адрес)')


# Заносим адреса в data и уведомляем пользователя о начале работы с его кошельками
@dp.message_handler(state=ClientStatesGroup.balance_scan)
async def addresses_checker(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['adds'] = msg.text

    if data['network'] == 'arb':
        checker_choice = arb_checker
    elif data['network'] == 'bsc':
        checker_choice = bsc_checker
    elif data['network'] == 'eth':
        checker_choice = eth_checker
    elif data['network'] == 'pol':
        checker_choice = pol_checker
    elif data['network'] == 'test':
        checker_choice = test_checker
    else:
        await msg.answer('Допущена ошибка при вводе. Попробуйте ввести сеть еще раз.')
        await ClientStatesGroup.network_scan.set()

    await bot.send_message(msg.from_user.id, 'Проверяю баланс')
    balance_info = asyncio.create_task(checker_choice(data['adds']))
    balance_info_f = await balance_info
    msg_for_send = asyncio.create_task(msg_sender(msg ,balance_info_f))
    msg_for_send_f = await msg_for_send
    await bot.send_message(msg.from_user.id, 'Все кошельки проверены.', reply_markup=check_keyboard)
    await state.finish()


# Пока не реализованная функция. Нужно сделать красивое оформление и if для свапа валют местами, если кидает ошибку.
@dp.message_handler()
async def price_checker(msg: types.message):
    pass
    # await bot.send_message(msg.from_user.id, 'Временно отсутствует')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
