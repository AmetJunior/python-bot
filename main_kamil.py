import logging
import requests
import json
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
BASE_URL = "http://45.130.43.65:9090/posts"

async def get_free_spaces():
    new_array = []
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL) as resp:
            let2 = json.loads(await resp.text())
            for elements in let2:
                if(elements.get('index_city') == 95000):
                    new_array.append([
                    elements['User_number_of_free_place_parking'],
                    elements['owner_name_parking'], 
                    elements['owner_free_forinvalid'], 
                    elements["owner_price_parking"]])
    if choose_true == elements['User_number_of_free_place_parking']:
            print("hello")
            elements['User_number_of_free_place_parking'] -= 1
            async with aiohttp.ClientSession() as session:
                await session.put(f"{BASE_URL}/{elements['id']}", data=json.dumps(elements))
    return new_array



# log
logging.basicConfig(level=logging.INFO)
# Оплата 
PRICE = types.LabeledPrice(label='бронь', amount = 100*100)
# Объект бота
bot = Bot(token="5812078222:AAHLp8IoHMYDJVrVuGStrxAjALUUZXd1h6g")
# Диспетчер
dp = Dispatcher(bot) 
# Переменная брони парковки
choose_booking = "0"


#на команду /start
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):

    ickb = [
        [types.KeyboardButton(text="Узнать кол-во свободных мест")],
        [types.KeyboardButton(text="Узнать есть ли льготные места")],
        [types.KeyboardButton(text="Забронировать место")]
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=ickb)
    await message.answer("Здравствуйте! Это телеграм бот проекта simfparking!\nЯ помогу вам узнать количество свободных мест и забронировать безналичным рассчетом.", reply_markup=keyboard)


#свободные места
@dp.message_handler(text=["Узнать кол-во свободных мест"])
async def cmd_free(message: types.Message):
    free_spaces = await get_free_spaces()
    print(free_spaces)
    for element in free_spaces:
        if(element[2] == True):
            element[2] = 'Доступны'
        else:
            element[2] = 'Не доступны'
        await message.answer(f"Cвободные места: {str(element[0])} на  {str(element[1])} в г.Симферополь.  Цена:{str(element[3])} руб")
#ячейкамассива1 ячейкамассива2 итд

@dp.message_handler(text=["Узнать есть ли льготные места"])
async def cmd_free1(message: types.Message):
    free_spaces = await get_free_spaces()
    for element in free_spaces:
        if(element[2] == True):
            element[2] = 'Доступны'
        else:
            element[2] = 'Не доступны'
        await message.answer(f"Льготные места: {str(element[2])}  на {str(element[1])} в г.Симферополь")


#задаем параметры окна покупкі
@dp.message_handler(text=['Забронировать место'])
async def cmd_start(message: types.Message):
    free_spaces = await get_free_spaces()
    freespace = []
    for element in free_spaces:
        ikb = [
        freespace.append([types.KeyboardButton(text=f"{str(element[1])}")])
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=freespace)
    await message.answer("выбери место)", reply_markup=keyboard)
    for element in free_spaces:
        name = element[1]
        @dp.message_handler(text=f"{str(element[1])}")
        async def button_booking(message: types.Message):
            global choose_booking
            x =  str(message['text'])
            choose_booking = x
            await bot.send_invoice(
            message.chat.id,
            title="Бронь места",
            description="Сейчас вы можете забронировать место на парковке, чтобы это сделать, вам надо заплатить 100 рублей в качестве залога :)",
            provider_token='381764678:TEST:49573',
            currency='rub',
            photo_url='https://media.istockphoto.com/vectors/car-parking-illustration-vector-id876792570?k=20&m=876792570&s=612x612&w=0&h=A0yUvnBbN0EFKpW1uYajpa1ycSHI0pGAGSqNHRd-GQo=',
            photo_height=512,
            photo_width=512,
            photo_size=512,
            is_flexible=False, 
            prices=[PRICE],
            start_parameter='time-machine-example',
            payload='some-invoice-payload-for-our-internal-use'
        )
            print('TET', choose_booking) 
        
    await message.answer("вернуться назад - /start", )




#препроверка
@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

#конечная обработка платежа(можно задать действия по совершению платежа!!)
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    global choose_true
    choose_true = choose_booking
    
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")
 
    await bot.send_message(message.chat.id,
                           f"Платёж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} по заказу места на "+ choose_booking +" прошел успешно!!!")


# Запуск процесса поллинга новых апдейтов
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
