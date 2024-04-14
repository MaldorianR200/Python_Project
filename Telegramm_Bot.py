import logging  # уровень логов
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext #  FSMContext для хранения информации о выбранном дне недели в течение сеанса чата
from aiogram.dispatcher.filters.state import State, StatesGroup
TOKEN_API =  "6868760353:AAGPJzkReqYKX0XdxbePeSmxvRKtrVYjPAI" # токен
# Устанавливаем уровень логов
logging.basicConfig(level=logging.INFO)

# Задание - план на неделю

HELP_COMMAND = """
<b>/help</b> - <em>список комманд</em>
<b>/start</b> - <em>начать работу с ботом</em>
<b>/plan</b> - <em>текущий план на указанный день недели</em>
<b>/setplan</b> - <em>установка плана на указанный день</em>
"""
# Определение состояний Бота
async def on_startup(_):
    print("Бот был успешно запущен!")

bot = Bot(TOKEN_API)    # создание бота
storage = MemoryStorage() # # Используем MemoryStorage для хранения состояний
dp = Dispatcher(bot, storage=storage) # диспетчер, отслеживание
dp.middleware.setup(LoggingMiddleware()) # отслеживаем работу бота

class SetDayState(StatesGroup): # опеределение состояния WAITING_FOR_DAY(обрабатка последующи[ действия пользователя )
    WAITING_FOR_DAY = State()

# Функция для чтения плана на конкретный день из файла
def read_plan_for_day(day, file):
    try:
        with open(file, "r") as plan_file:  # открываем файл для чтения
            # Читаем все строки из файла
            lines = plan_file.readlines()
            plan = ""   # инициализируем переменную для храниея плана
            print(lines)
            # Перебираем строки и ищем план для указанного дня
            if len(lines) != 0:
                for line in lines:
                    # План записывается в формате "День: План"
                    plan += ' '.join(line.split()) + '\n'
                    #print(plan)
                return plan # возвращаем план
            else:
                return "План на этот день не найден."
    except FileNotFoundError:
        return "Вы ещё не добавили план для этого дня!"


# Функция для сохранения плана на понедельник
def save_plan_for_monday(plan_text, mode):
    with open("plan_monday.txt", mode) as plan_file:
        plan_file.write(plan_text + "\n")

# Функция для сохранения плана на вторник
def save_plan_for_tuesday(plan_text, mode):
    with open("plan_tuesday.txt", mode) as plan_file:
        plan_file.write(plan_text + "\n")

# Функция для сохранения плана на среду
def save_plan_for_wednesday(plan_text, mode):
    with open("plan_wednesday.txt", mode) as plan_file:
        plan_file.write(plan_text + "\n")

# Функция для сохранения плана на четверг
def save_plan_for_thursday(plan_text, mode):
    with open("plan_thursday.txt", mode) as plan_file:  # открываем файл plan_thursday.txt и сохраняем туда план пользователя
        plan_file.write(plan_text + "\n")

# Функция для сохранения плана на пятницу
def save_plan_for_friday(plan_text, mode):
    with open("plan_friday.txt", mode) as plan_file:
        plan_file.write(plan_text + "\n")

# Функция для сохранения плана на субботу
def save_plan_for_saturday(plan_text, mode):
    with open("plan_saturday.txt", mode) as plan_file:
        plan_file.write(plan_text + "\n")

# Функция для сохранения плана на воскресенье
def save_plan_for_sunday(plan_text, mode):
    with open("plan_sunday.txt", mode) as plan_file:
        plan_file.write(plan_text + "\n")


# Команда /help - выводит список всех команд
@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=HELP_COMMAND,
                           parse_mode="HTML",
                          )
    await message.delete() # удаляем сообщение /help

# Команда /start - приветствует пользователя и предлагает начать работу
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_name = message.from_user.first_name    # имя пользователя
    await message.reply(f"Привет, {user_name}! Я бот-помощник для создания плана на неделю. "
                        "Чтобы начать, введите команду /setplan или /help для просмотра всех "
                        "доступных команд")


# # Обработчик для текстовых сообщений, которые не были обработаны другими обработчиками
# @dp.message_handler()
# async def handle_text(message: types.Message):
#     # Проверяем, содержит ли сообщение только текст
#     if message.text.strip() != "":
#         # Если сообщение содержит текст, но не было обработано другими обработчиками,
#         # отправляем пользователю сообщение о том, что его ввод не распознан
#         await message.reply("Введена неизвестная команда!. Пожалуйста, воспользуйтесь доступными командами или функциями бота.")
#     # Если сообщение пустое (например, пользователь отправил только пробелы), игнорируем его


# Команда /plan - выводит план для конкретного дня
@dp.message_handler(commands=['plan'])
async def process_plan_command(message: types.Message):
    # Создаем клавиатуру с кнопками дней недели
    keyboard = InlineKeyboardMarkup(row_width=2)
    # Список дней недели
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    # создание списка кнопок
    buttons = [InlineKeyboardButton(text=day, callback_data=f"plan_{day}") for day in days]
    # добавляем список кнопок в клавиатуру
    keyboard.add(*buttons)  # распаковки итерируемых объектов
    await message.reply("Выберите день недели для просмотра плана:", reply_markup=keyboard)
    await message.delete()


# Обработка выбора дня недели для просмотра плана
@dp.callback_query_handler(lambda query: query.data.startswith('plan_'))
async def process_plan_day(callback_query: types.CallbackQuery):
    # делим строку на две части и выбираем второую, т.к. там содержится день недели
    day = callback_query.data.split('_')[1]
    plan = ""
    # Обрабатываем выбранного дня (счиытваем данные из файла, в зависимости от дня недели)
    if day == "Понедельник":
        plan = read_plan_for_day(day, "plan_monday.txt")
    elif day == "Вторник":
        plan = read_plan_for_day(day, "plan_tuesday.txt")
    elif day == "Среда":
        plan = read_plan_for_day(day, "plan_wednesday.txt")
    elif day == "Четверг":
        plan = read_plan_for_day(day, "plan_thursday.txt")
    elif day == "Пятница":
        plan = read_plan_for_day(day, "plan_friday.txt")
    elif day == "Суббота":
        plan = read_plan_for_day(day, "plan_saturday.txt")
    elif day == "Воскресенье":
        plan = read_plan_for_day(day, "plan_sunday.txt")

    # вывод плана
    await bot.send_message(callback_query.from_user.id, f"План на выбранный день:\n{plan}")


# Обработка выбора пользователя по добавлению или замене плана
@dp.callback_query_handler(lambda query: query.data in ["add_plan", "replace_plan"])
async def process_plan_option(callback_query: types.CallbackQuery, state: FSMContext):
    plan_option = callback_query.data

    # Получаем выбранный день из состояния чата
    async with state.proxy() as data:
        selected_day = data['selected_day']
    # обрабатываем опцию, которую выбрал пользователь
    if plan_option == "add_plan":
        await bot.send_message(callback_query.from_user.id, f"Введите ваш план для {selected_day}."
                                                            " Он будет добавлен к текущему плану.")
    elif plan_option == "replace_plan":
        await bot.send_message(callback_query.from_user.id, f"Введите ваш новый план для {selected_day}."
                                                            " Он заменит текущий план.")

    # Сохраняем выбранную опцию в состоянии чата
    await state.update_data(plan_option=plan_option)
    print(plan_option)
    await SetDayState.WAITING_FOR_DAY.set()

# Обработка выбора дня недели
@dp.callback_query_handler(lambda query: query.data.startswith('day_'))
async def process_day(callback_query: types.CallbackQuery, state: FSMContext):

    # Спрашиваем пользователя, будет ли он добавлять новый план или заменять текущий
    keyboard = InlineKeyboardMarkup()   # инициализируем клавиатуру
    # создаём список кнопок
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data="add_plan"),
        InlineKeyboardButton(text="Заменить", callback_data="replace_plan")
    ]
    keyboard.add(*buttons)
    day = callback_query.data.split('_')[1]
    #print(day)
    # await bot.send_message(callback_query.from_user.id, f"Выбран день: {day}. Теперь введите свой план.")
    await bot.send_message(callback_query.from_user.id, "Хотите добавить этот план к текущим записям или заменить их?", reply_markup=keyboard)

    # Сохраняем выбранный день в состоянии чата
    await state.update_data(selected_day=day)

# Получаем выбранный день и опцию плана из состояния чата
@dp.message_handler(state=SetDayState.WAITING_FOR_DAY)
async def process_plan(message: types.Message, state: FSMContext):

    selected_day = ""   # выбранный день
    plan_option = ""    # выбранная опция
    print("Обработка текствого сообщения!!!")
    # Получаем выбранный день из состояния чата
    async with state.proxy() as data:
        plan_option = data['plan_option']
        selected_day = data['selected_day']
        print(selected_day)
    # Сохраняем план в файл
    if selected_day:    # проверяем условие
        if selected_day == "Понедельник":
            if plan_option == "add_plan":
                save_plan_for_monday(message.text, 'a')
            elif plan_option == "replace_plan":
                save_plan_for_monday(message.text, 'w')

        elif selected_day == "Вторник":
            if plan_option == "add_plan":
                save_plan_for_tuesday(message.text, 'a')
            elif plan_option == "replace_plan":
                save_plan_for_tuesday(message.text, 'w')

        elif selected_day == "Среда":
            if plan_option == "add_plan":
                save_plan_for_wednesday(message.text, 'a')
            elif plan_option == "replace_plan":
                save_plan_for_wednesday(message.text, 'w')

        elif selected_day == "Четверг":
            if plan_option == "add_plan":
                save_plan_for_thursday(message.text, 'a')
            elif plan_option == "replace_plan":
                save_plan_for_thursday(message.text, 'w')

        elif selected_day == "Пятница":
            if plan_option == "add_plan":
                save_plan_for_friday(message.text, 'a')
            elif plan_option == "replace_plan":
                save_plan_for_friday(message.text, 'w')

        elif selected_day == "Суббота":
            if plan_option == "add_plan":
                save_plan_for_saturday(message.text, 'a')
            elif plan_option == "replace_plan":
                save_plan_for_saturday(message.text, 'w')
        elif selected_day == "Воскресенье":
            if plan_option == "add_plan":
                save_plan_for_sunday(message.text, 'a')
            elif plan_option == "replace_plan":
                save_plan_for_sunday(message.text, 'w')

        await message.reply(f"План на {selected_day} сохранен.")
        await state.finish() # очищаем состояние после сохранения плана
    else:
        await message.reply("Ошибка: Выбранный день не определен. Пожалуйста, выберите день снова.")



# Команда /setplan - выбираем день недели и прописываем план
@dp.message_handler(commands=['setplan'])
async def set_plan(message: types.Message):
    # Создаем клавиатуру с кнопками дней недели
    keyboard = InlineKeyboardMarkup(row_width=2)
    # список дней недели
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    # создаём список кнопок
    buttons = [InlineKeyboardButton(text=day, callback_data=f"day_{day}") for day in days]
    keyboard.add(*buttons)
    await message.reply("Выберите день недели:", reply_markup=keyboard)
    await message.delete()
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)








