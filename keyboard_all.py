from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# Начальная клавиатура.
button_balance_check, button_token_sender = KeyboardButton('Баланс'), KeyboardButton('Отправить токен')
check_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
check_keyboard.add(button_balance_check, button_token_sender)


#Клавиатура чекера балансов и сендера
button_balance_bsc, button_balance_arb = KeyboardButton('BSC'), KeyboardButton('ARB')
button_balance_eth, button_balance_pol = KeyboardButton('ETH'),KeyboardButton('POL')
button_cancel = KeyboardButton('/cancel')
button_balance_test = KeyboardButton('test') # Удалить или скрыть после тестов
balance_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
balance_keyboard.add(button_balance_bsc, button_balance_arb)
balance_keyboard.add(button_balance_eth, button_balance_pol)
balance_keyboard.add(button_balance_test) # Удалить или скрыть после тестов
balance_keyboard.add(button_cancel)
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.add(button_cancel)
sender_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
sender_keyboard.add(button_balance_bsc, button_balance_eth)
sender_keyboard.add(button_balance_test) # Удалить или скрыть после тестов
sender_keyboard.add(button_cancel)