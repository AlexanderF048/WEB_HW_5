import sys
import platform
import datetime
import logging

import asyncio
import aiohttp
import websockets
import json
import pprint

logging.basicConfig(level=logging.INFO)


async def start_input_handler(max_date_range: int = 10) -> tuple:
    asking_dates = []
    if 0 < int(sys.argv[1]) <= max_date_range:

        minus_date_counter = 1

        for i in range(int(sys.argv[1])):
            i_date = datetime.date.today() - datetime.timedelta(days=minus_date_counter)
            minus_date_counter += 1
            asking_dates.append(i_date.strftime('%d.%m.%Y'))
    else:
        logging.error(f'SMTH went wrong, please notice - input example: py main.py 10, '
                      f'where 10 is max amount of requested dates. ')

    asking_dates_tuple = (*asking_dates,)  # Распаковка списка в кортеж
    logging.info(f"Asking_dates_tuple was created: {asking_dates_tuple}")

    return asking_dates_tuple


# ----------------

async def url_builder(dates: tuple) -> tuple:
    return tuple([f'https://api.privatbank.ua/p24api/exchange_rates?json&date={x_date}' for x_date in dates])


# ----------------

async def currency_client(asking_urls: tuple):
    print(f'Client got {asking_urls}')
    request_output = []
    # downloaded = []

    async with aiohttp.ClientSession() as session:
        task_s = []
        for url in asking_urls:
            task = asyncio.create_task(session.get(url))
            task_s.append(task)
        done_tasks = await asyncio.gather(*task_s)

        for i in done_tasks:
            json_data = await i.json()
            request_output.append(json_data)

        return request_output

        # ----Альтернативный код-----
        # for url in asking_urls:
        ###### async with [session.get(url) for url in asking_urls] as response: # НЕ РАБОТАЕТ !
        # async with session.get(url) as response:
        #    print("Status:", response.status)
        #    print("Content-type:", response.headers['content-type'])
        #    print('Cookies: ', response.cookies)
        #    print(response.ok)
        #
        # downloaded.append(await response.json())


# ----------------

async def currency_handler(currency_list, cur=('USD', 'EUR')):
    output_list = []

    for date in currency_list:
        out_cur_dict = {date['date']: {}}

        for i in date['exchangeRate']:
            #print(i)

            for req_cur in cur:
                if req_cur in i.values():
                    formatted = {i['currency']: {'sale': i['saleRateNB'], 'purchase': i['purchaseRateNB']}}
                    #print(formatted)

                    out_cur_dict[date['date']].update(formatted)
                    output_list.append(out_cur_dict)
    return output_list


# ----------------


async def main():
    dates_to_check: tuple = await start_input_handler()
    #print(dates_to_check)

    url_to_check: tuple = await url_builder(dates_to_check)
    #print(url_to_check)

    received_data = await currency_client(url_to_check)
    #print(received_data)

    output = await currency_handler(received_data)

    return output


if __name__ == '__main__':

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    r = asyncio.run(main())
    print(r)

    exit()
