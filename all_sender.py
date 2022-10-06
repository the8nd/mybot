from web3 import Web3
from abi_links_contracts import *
from aiogram.utils.markdown import hlink
import decimal
import time
import datetime


# В файле располагаются все сендеры, которые бот использует.
# Переписать код сендера, чтобы использовать одну и ту же часть для разных сетей. Оптимизировать его.
# Обработка ошибки не отправленной транзакции.


async def token_sender(all_info):
    # Создание всех нужных переменных
    token_to_send = all_info['token']
    sender_adds = all_info['sender_adds']
    sender_adds = sender_adds.split('\n')
    sender_private = all_info['sender_private']
    sender_private = sender_private.split('\n')
    amount_to_send = all_info['amount']
    reciever_adds = all_info['reciever']
    reciever_adds = reciever_adds.split('\n')
    hash_result = []
    counter = 1
    sender_counter = 0
    reciever_counter = 0
    bool_sender = True
    bool_reciever = True
    native_token = True

    # Определяем какой метод рассылки будет использоваться
    # 1 > many
    if len(sender_adds) == 1 and len(sender_private) == 1:
        time_hold = 10
        bool_sender = False
    # many > many
    elif len(sender_adds) == len(reciever_adds) == len(sender_private):
        time_hold = 0

    # many > 1
    elif len(reciever_adds) == 1 and len(sender_adds) == len(sender_private):
        time_hold = 0
        bool_reciever = False
    # Если кол-во адресов и приватных ключей не равно друг другу.
    else:
        hash_result.append('Количество адресов или приватных ключей не совпадает. Попытайтесь снова.')
        return hash_result

    # Ищем самый длинный массив, чтобы использовать его для цикла
    if len(sender_adds) >= len(reciever_adds):
        o = len(sender_adds)
    else:
        o = len(reciever_adds)

    # Выбираем нужную сеть, нужный контракт и нужную часть кода.
    if all_info['network'] == 'eth':
        print('ETH test')
        web3 = Web3(Web3.HTTPProvider(ethereum_link))  # Подключаемся к eth_link
        gas = all_info['gas']
        gwei = all_info['gwei']
        chain_id = 1

        if token_to_send == 'eth':
            token_name = 'ETH'
        elif token_to_send == 'usdt':
            token_name = 'USDT'
            token_contract = usdt_eth
            token_abi = usdt_eth_abi
            native_token = False
        else:
            hash_result.append('Данный токен не поддерживается сетью.')
            return hash_result

    elif all_info['network'] == 'bsc':
        web3 = Web3(Web3.HTTPProvider(bsc_link))  # Подключаемся к bsc_link
        gas = 75000
        gwei = 5
        chain_id = 56

        if token_to_send == 'usdt':
            token_name = 'USDT'
            token_contract = usdt_bsc
            token_abi = usdt_bsc_abi
            native_token = False
        elif token_to_send == 'busd':
            token_name = 'BUSD'
            token_contract = busd_bsc
            token_abi = busd_bsc_abi
            native_token = False
        elif token_to_send == 'bnb':
            token_name = 'BNB'
        else:
            hash_result.append('Данный токен не поддерживается сетью.')
            return hash_result


    if native_token == True:
        sender_add = ''
        for i in range(o):
            try:
                sender_add = web3.toChecksumAddress(sender_adds[sender_counter])  # Превращаем в checksum
                reciever_add = web3.toChecksumAddress(reciever_adds[reciever_counter])
                nonce = web3.eth.getTransactionCount(sender_add)
                token_tx = {
                    'nonce': nonce,
                    'to': reciever_add,
                    'value': web3.toWei(amount_to_send, 'ether'),
                    'gas': gas,
                    'gasPrice': web3.toWei(gwei, 'gwei')
                }
                sign_tx = web3.eth.account.signTransaction(token_tx, sender_private[sender_counter])
                tx_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)
                tx_link = hlink('Ссылка', f'https://bscscan.com/tx/{web3.toHex(tx_hash)}')
                hash_result.append(
                    f'<b>{counter}</b>\n<b>Хэш:</b> {tx_link}\n<b>Отправлено:</b> {amount_to_send} BNB\n<b>Отправитель:</b> {sender_add}\n<b>Получатель:</b> {reciever_add}')
                time.sleep(time_hold)
            except ValueError:
                hash_result.append(
                    f'<b>{counter}</b>\n{sender_add}\nНа кошельке недостаточно средств для оплаты комиссии, либо прошлая транзакция неуспела обработаться. Попытайтесь снова.')
            except decimal.InvalidOperation:
                hash_result.append(f'<b>{counter}</b>\n{sender_add}\nВы ввели текст вместо суммы. Попробуйте еще раз.')
                return hash_result

            counter += 1
            if bool_sender == True:
                sender_counter += 1
            elif bool_reciever == True:
                reciever_counter += 1


    elif native_token == False:
        sender_add = ''
        for i in range(o):
            try:
                sender_add = web3.toChecksumAddress(sender_adds[sender_counter])
                reciever_add = web3.toChecksumAddress(reciever_adds[reciever_counter])
                nonce = web3.eth.getTransactionCount(sender_add)
                amount_to_send_ether = web3.toWei(amount_to_send, 'ether')
                token_contract_final = web3.eth.contract(address=token_contract, abi=token_abi)
                token_tx = token_contract_final.functions.transfer(reciever_add, amount_to_send_ether).buildTransaction(
                    {
                        'chainId': chain_id,
                        'gas': gas,
                        'gasPrice': web3.toWei(gwei, 'gwei'),
                        'nonce': nonce
                    })
                sign_tx = web3.eth.account.signTransaction(token_tx, sender_private[sender_counter])
                tx_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)
                tx_link = hlink('Ссылка', f'https://bscscan.com/tx/{web3.toHex(tx_hash)}')
                hash_result.append(
                    f'<b>{counter}</b>\n<b>Хэш:</b> {tx_link}\n<b>Отправлено:</b> {amount_to_send} {token_name} \n<b>Отправитель:</b> {sender_add}\n<b>Получатель:</b> {reciever_add}')
                time.sleep(time_hold)
            except ValueError:
                hash_result.append(
                    f'<b>{counter}</b>\n{sender_add}\nНа кошельке недостаточно средств для оплаты комиссии, либо прошлая транзакция неуспела обработаться. Попытайтесь снова.')
            except decimal.InvalidOperation:
                hash_result.append(f'<b>{counter}</b>\n{sender_add}\nВы ввели текст вместо суммы. Попробуйте еще раз.')
                return hash_result

            counter += 1
            if bool_sender == True:
                sender_counter += 1
            if bool_reciever == True:
                reciever_counter += 1

    hash_result.append('Все отправлено.')
    return hash_result