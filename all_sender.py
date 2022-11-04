import asyncio

from web3 import Web3
from web3.exceptions import TransactionNotFound

from abi_links_contracts import *
from aiogram.utils.markdown import hlink
import decimal
import logging


# В файле располагаются все сендеры, которые бот использует.
# Переписать код сендера, чтобы использовать одну и ту же часть для разных сетей. Оптимизировать его.
# Обработка ошибки не отправленной транзакции.

async def tx_checker(hash, web_link):
    counter = 0
    web3 = Web3(Web3.HTTPProvider(web_link))
    while True:
        try:
            result_tx = web3.eth.get_transaction(hash)
            if result_tx['blockHash'] is None:
                await asyncio.sleep(0.2)
            else:
                break
        except TransactionNotFound:
            counter += 1
            if counter == 20:
                break


async def token_sender(all_info):
    # Создание всех нужных переменных
    logging.info(all_info)
    token_to_send = all_info['token']
    sender_adds = all_info['sender_adds']
    sender_adds = sender_adds.split('\n')
    sender_private = all_info['sender_private']
    sender_private = sender_private.split('\n')
    amount_to_send = all_info['amount']
    reciever_adds = all_info['reciever']
    reciever_adds = reciever_adds.split('\n')
    hash_result = []
    sender_counter = 0
    reciever_counter = 0
    bool_sender = True
    bool_reciever = True
    bool_many = True # Если отправляем many>many или many>1 нет смысла ждать транзу
    native_token = True

    # Определяем какой метод рассылки будет использоваться
    # 1 > many
    if len(sender_adds) == 1 and len(sender_private) == 1:
        bool_sender = False
        bool_many = False
    # many > many проверяем, что кол-во везде равно.
    elif len(sender_adds) == len(reciever_adds) == len(sender_private):
        pass
    # many > 1
    elif len(reciever_adds) == 1 and len(sender_adds) == len(sender_private):
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
        web3 = Web3(Web3.HTTPProvider(ethereum_link))  # Подключаемся к eth_link
        link = ethereum_link
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

    elif all_info['network'] == 'bsc':
        web3 = Web3(Web3.HTTPProvider(bsc_link))
        link = bsc_link# Подключаемся к bsc_link
        gas = all_info['gas']
        gwei = all_info['gwei']
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

    # Удалить или скрыть после тестов
    elif all_info['network'] == 'test':
        link = test_link
        web3 = Web3(Web3.HTTPProvider(test_link))
        gas = 100000
        gwei = 20
        chain_id = 97
        token_name = 'BNB'

    if native_token:
        sender_add = ''
        logging.info('-'*20)
        for i in range(o):
            try:
                sender_add = web3.toChecksumAddress((sender_adds[sender_counter]).strip())  # Превращаем в checksum
                reciever_add = web3.toChecksumAddress((reciever_adds[reciever_counter]).strip())
                nonce = web3.eth.getTransactionCount(sender_add)
                token_tx = {
                    'nonce': nonce,
                    'to': reciever_add,
                    'value': web3.toWei(amount_to_send, 'ether'),
                    'gas': int(gas),
                    'gasPrice': web3.toWei(gwei, 'gwei')
                }
                sign_tx = web3.eth.account.signTransaction(token_tx, (sender_private[sender_counter]).strip())
                tx_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)
                # tx_link = hlink('Ссылка', f'https://bscscan.com/tx/{web3.toHex(tx_hash)}')
                # Потом вернуть на место и сделать для эфира
                logging.info(all_info['username'])
                logging.info(all_info['id'])
                logging.info(all_info['network'])
                logging.info(f'Sender: {sender_add}')
                logging.info(f'Reciever: {reciever_add}')
                logging.info(f'Hash: {web3.toHex(tx_hash)}')
                logging.info('-'*20)
                hash_result.append(
                    f'<b>{i+1}</b> <b>Хэш:</b> {web3.toHex(tx_hash)}\n<b>Отправлено:</b> {amount_to_send} BNB\n'
                    f'<b>Отправитель:</b> {sender_add}\n<b>Получатель:</b> {reciever_add}')
                if not bool_many:
                    tx_hash_result = asyncio.create_task(tx_checker(tx_hash, link))
                    tx_hash_result_f = await tx_hash_result

            except ValueError:
                logging.info(all_info['username'])
                logging.info(all_info['id'])
                logging.info(all_info['network'])
                logging.info(f'Sender: {sender_add}')
                logging.info(f'Reciever: {reciever_add}')
                logging.info('ValueError')
                logging.info('-'*20)
                hash_result.append(
                    f'<b>{i+1}</b>\n{sender_add}\nНа кошельке недостаточно средств для оплаты комиссии,'
                    f' либо прошлая транзакция неуспела обработаться. Попытайтесь снова.')
            except decimal.InvalidOperation:
                logging.info(all_info['username'])
                logging.info(all_info['id'])
                logging.info(all_info['network'])
                logging.info(f'Sender: {sender_add}')
                logging.info(f'Reciever: {reciever_add}')
                logging.info('decimal error')
                logging.info('-'*20)
                hash_result.append(f'<b>{i+1}</b>\n{sender_add}\nВы ввели текст вместо суммы. Попробуйте еще раз.')
                return hash_result

            if bool_sender:
                sender_counter += 1
            if bool_reciever:
                reciever_counter += 1

    elif not native_token:
        sender_add = ''
        for i in range(o):
            try:
                sender_add = web3.toChecksumAddress((sender_adds[sender_counter]).strip())
                reciever_add = web3.toChecksumAddress((reciever_adds[reciever_counter]).strip())
                nonce = web3.eth.getTransactionCount(sender_add)
                amount_to_send_ether = web3.toWei(amount_to_send, 'ether')
                token_contract_final = web3.eth.contract(address=token_contract, abi=token_abi)
                token_tx = token_contract_final.functions.transfer(reciever_add, amount_to_send_ether).buildTransaction(
                    {
                        'chainId': chain_id,
                        'gas': int(gas),
                        'gasPrice': web3.toWei(gwei, 'gwei'),
                        'nonce': nonce
                    })
                sign_tx = web3.eth.account.signTransaction(token_tx, (sender_private[sender_counter]).strip())
                tx_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)
                tx_link = hlink('Ссылка', f'https://bscscan.com/tx/{web3.toHex(tx_hash)}')
                logging.info(all_info['username'])
                logging.info(all_info['id'])
                logging.info(all_info['network'])
                logging.info(f'Sender: {sender_add}')
                logging.info(f'Reciever: {reciever_add}')
                logging.info(f'Hash: {web3.toHex(tx_hash)}')
                logging.info('-'*20)
                hash_result.append(
                    f'<b>{i+1}</b>\n<b>Хэш:</b> {tx_link}\n<b>Отправлено:</b> {amount_to_send} {token_name} \n'
                    f'<b>Отправитель:</b> {sender_add}\n<b>Получатель:</b> {reciever_add}')
                if not bool_many:
                    tx_hash_result = asyncio.create_task(tx_checker(tx_hash, link))
                    tx_hash_result_f = await tx_hash_result
            except ValueError:
                logging.info(all_info['username'])
                logging.info(all_info['id'])
                logging.info(all_info['network'])
                logging.info(f'Sender: {sender_add}')
                logging.info(f'Reciever: {reciever_add}')
                logging.info('ValueError')
                logging.info('-'*20)
                hash_result.append(
                    f'<b>{i+1}</b>\n{sender_add}\nНа кошельке недостаточно средств для оплаты комиссии, '
                    f'либо прошлая транзакция неуспела обработаться. Попытайтесь снова.')
            except decimal.InvalidOperation:
                logging.info(all_info['username'])
                logging.info(all_info['id'])
                logging.info(all_info['network'])
                logging.info(f'Sender: {sender_add}')
                logging.info(f'Reciever: {reciever_add}')
                logging.info('decimal error')
                logging.info('-'*20)
                hash_result.append(f'<b>{i+1}</b>\n{sender_add}\nВы ввели текст вместо суммы. Попробуйте еще раз.')
                return hash_result

            if bool_sender:
                sender_counter += 1
            if bool_reciever:
                reciever_counter += 1

    hash_result.append('Все отправлено.')
    return hash_result
