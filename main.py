import time
from selenium import webdriver

# Define some constants
url = 'http://silver-bk.com'
username = 'justme'
password = '123qwe'

# Bot exceptions
class BotError(Exception): pass
class BotUsageError(BotError): pass
class BotParsingError(BotError): pass


# Set browser
browser = webdriver.Chrome('C:\\chromedriver\\chromedriver.exe')
#browser = webdriver.PhantomJS('C:\\phantomjs\\bin\\phantomjs.exe')
#browser.set_window_size(1366, 728)
browser.set_window_size(1034, 619)


def authorization():
    browser.get(url)
    inputs = browser.find_elements_by_tag_name('input')
    inputs[0].send_keys(username)
    inputs[1].send_keys(password)
    inputs[2].click()


def screenshot(filename=None):
    now = time.localtime()
    if filename is None:
        filename = ("Screenshot_{0.tm_year}-{0.tm_mon:02}-{0.tm_mday:02}_"
                    "{0.tm_hour:02}{0.tm_min:02}{0.tm_sec:02}"
                    ".png".format(now))
    print("Saving screenshot '" + filename + "'")
    browser.save_screenshot(filename)

### Функции "До похода" ###

caverns = [
    "Канализация",
    "ПТП",
    "Бездна",
    "Грибница",
    "Пещера мглы",
    "Ледяная пещера",
    "Излом Хаоса",
    "Сторожевая Башня",
    "Потерянный вход",
    "Катакомбы"]

## Вспомогательные функции ##

def select_main_frame():
    try:
        frames = browser.find_elements_by_tag_name('frame')
        main_frame = frames[[frame.get_attribute('name')
                             for frame in frames].index('main')]
        browser.switch_to.frame(main_frame)
    except (ValueError, KeyError):
        raise BotParsingError        


# From main screen only
def click_cavern(cavern_name):
    try:
        cavern_id = caverns.index(cavern_name)
    except ValueError:
        raise BotUsageError("Неверное имя пещеры!")
    
    # Select link to cavern
    try:
        links = browser.find_elements_by_tag_name('a')
        cavern_link = None
        for link in links:
            if link.get_attribute('href').endswith('portal.php?go={}'.format(
                cavern_id)):
                cavern_link = link
        cavern_link.click()
        
    except (ValueError, KeyError, AttributeError):
        raise BotParsingError


# From tasks screen only
def click_button(value):
    try:
        inputs = browser.find_elements_by_tag_name('input')
        button = inputs[[x.get_attribute('value')
                               for x in inputs].index(value)]
        button.click()
        time.sleep(1)

    except (ValueError, KeyError):
        raise BotParsingError


def click_link(text):
    try:
        links = browser.find_elements_by_tag_name('a')
        link = links[[x.text for x in links].index(text)]
        link.click()
        time.sleep(1)

    except (ValueError, KeyError):
        raise BotParsingError
 
    



# 1. Получить задание
def get_task(cavern_name):
    click_cavern(cavern_name)
    click_button('Задания')
    
    try:
        click_button('Получить задание')
    except BotParsingError:
        print("Заданий нет")

    click_button('Вернуться')
    click_link('Портал воспоминаний')


# 2. Начать прохождение
def enter_cavern(cavern_name):
    click_cavern(cavern_name)
    click_button('Создать группу')
    click_button('Начать')
    

### Функции прохождения пещеры ###

directions = {
    'forward':   'top',
    'backward':  'buttom',
    'left':      'left',
    'right':     'right',
    'rot-left':  'vlevo',
    'rot-right': 'vpravo',
    'refresh':   'ref'}

# 1. Перемещения и повороты
def move(direction):
    name = directions[direction]
    
    images = browser.find_elements_by_tag_name('img')
    direction_image = None
    for image in images:
        href = image.get_attribute('src')
        if href.endswith(name + '.gif') or href.endswith(name + 'i.gif'):
            direction_image = image
            break
        
    if image is None:
        raise BotParsingError
    else:
        image.click()
    time.sleep(2)


# 2. Атаковать монстра
def attack():
    images = browser.find_elements_by_tag_name('img')
    monsters = []
    for image in images:
        width = image.get_attribute('width')
        height = image.get_attribute('height')
        if width == '100' and height == '160':
            monsters.append(image)
    if len(monsters) > 0:
        print("Обнаружены монстры:")
        for no, monster in enumerate(monsters, 1):
            print("    {:2}. {}".format(no, monster.get_attribute('title')))

        monsters[0].click()
        click_link('Напасть')
    else:
        print("Монстры не обнаружены!")


# 3. Ждать восстановления здоровья
def wait_for_regeneration():
    while True:
        hp = browser.find_element_by_xpath('//*[@id="hp"]/div[2]/font/b')
        current_hp, max_hp = hp.text.split('/')
        if int(current_hp) == int(max_hp):
            break
        move('refresh')
        time.sleep(10)

    


# 4. Собрать предметы
def collect_one():
    images = browser.find_elements_by_tag_name('img')
    srcs = [x.get_attribute('src') for x in images]
    items = []
    for no, src in enumerate(srcs):
        if 'drop_items' in src:
            items.append(images[no])
    if len(items) > 0:
        items[0].click()
        return True
    else:
        return False

def collect_all():
    while collect_one():
        time.sleep(1)


# 5. Надеть комплект
def wear(name):
    browser.find_element_by_xpath('//*[@id="T5"]/a[2]/img').click()
    icon = browser.find_element_by_xpath('/html/body/form/table/tbody/'
        'tr/td[2]/table/tbody/tr/td/table[6]/tbody/tr/td[1]/a/img')
    if icon.get_attribute('src').endswith('plus.gif'):
        icon.click()
        

### Функции боя ###

# 1. Ударить
def punch(attack=0, defence=0):
    attack_buttons = []
    defence_buttons = []
    
    inputs = browser.find_elements_by_tag_name('input')
    for button in inputs:
        if button.get_attribute('type') == 'radio':
            if button.get_attribute('name') == 'attack':
                attack_buttons.append(button)
            if button.get_attribute('name') == 'defend':
                defence_buttons.append(button)

    attack_buttons[attack].click()
    defence_buttons[defence].click()
    click_button('Вперед !!!')        


# 2. Использовать приём
def use_ability(numbers={}):
    images = browser.find_elements_by_tag_name('img')
    srcs = [x.get_attribute('src') for x in images]
    abils = []
    for no, src in enumerate(srcs):
        if 'priem' in src:
            abils.append(images[no])
    for no, abil in enumerate(abils):
        if no in numbers:
            abil.click()

# 3. Закончить бой
def end_attack():
    click_button('Закончить')


def test_portal_ptp():
    authorization()
    select_main_frame()
    for cavern in caverns[1:3]:
        get_task(cavern)

def test_enter_cavern():
    enter_cavern('Канализация')

def test_move():
    authorization()
    select_main_frame()
    collect_all()


try:
    test_move()
except BotError as err:
    screenshot("bug.png")
    raise err
