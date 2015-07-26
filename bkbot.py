import selenium
import selenium.webdriver
import time


class BotError(Exception): pass
class BotUsageError(BotError): pass
class BotParsingError(BotError): pass


class Engine:

    CAVERNS = [
        'Канализация',
        'ПТП',
        'Бездна',
        'Грибница',
        'Пещера мглы',
        'Ледяная пещера',
        'Излом Хаоса',
        'Сторожевая Башня',
        'Потерянный вход',
        'Катакомбы',
        ]
    
    DIRECTIONS = {
        'forward':   'top',
        'backward':  'buttom',
        'left':      'left',
        'right':     'right',
        'turn_left':  'vlevo',
        'turn_right': 'vpravo',
        'refresh':   'ref'
        }
    
    URL = 'http://silver-bk.com'
    AUTHORIZATION_TIMEOUT = 1
    CLICK_BUTTON_TIMEOUT = 1
    CLICK_DIRECTION_BUTTON_TIMEOUT = 5
    CLICK_LINK_TIMEOUT = 1
    CLICK_ITEM_TIMEOUT = 1
    CLICK_OBJECT_TIMEOUT = 1
    CLICK_ABILITY_TIMEOUT = 1


    def __init__(self, silent=True):
        if silent:
            self.browser = selenium.webdriver.PhantomJS('drivers\\'
                                                        'phantomjs.exe')
        else:
            self.browser = selenium.webdriver.Chrome('drivers\\'
                                                     'chromedriver.exe')
        self.browser.set_window_size(1034, 619)


    def __enter__(self):
        return self


    def __exit__(self, tp, vl, tb):
        self.browser.quit()


    def authorization(self, username, password):
        self.browser.get(self.URL)
        inputs = self.browser.find_elements_by_tag_name('input')
        inputs[0].send_keys(username)
        inputs[1].send_keys(password)
        inputs[2].click()
        time.sleep(self.AUTHORIZATION_TIMEOUT)


    def click_ability(self, number):
        images = self.browser.find_elements_by_tag_name('img')
        srcs = [x.get_attribute('src') for x in images]
        abils = []
        for no, src in enumerate(srcs):
            if 'priem' in src:
                abils.append(images[no])
        abils[number].click()
        time.sleep(self.CLICK_ABILITY_TIMEOUT)


    def click_button(self, value):
        try:
            inputs = self.browser.find_elements_by_tag_name('input')
            button = inputs[[x.get_attribute('value')
                                   for x in inputs].index(value)]
            button.click()
            time.sleep(self.CLICK_BUTTON_TIMEOUT)

        except (ValueError, KeyError):
            raise BotParsingError


    def click_direction_button(self, direction):
        name = self.DIRECTIONS[direction]
        
        images = self.browser.find_elements_by_tag_name('img')
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
        time.sleep(self.CLICK_DIRECTION_BUTTON_TIMEOUT)


    def click_cavern(self, cavern_name):
        try:
            cavern_id = self.CAVERNS.index(cavern_name)
        except ValueError:
            raise BotUsageError("Неверное имя пещеры!")
        
        # Select link to cavern
        try:
            links = self.browser.find_elements_by_tag_name('a')
            cavern_link = None
            for link in links:
                if link.get_attribute('href').endswith(
                    'portal.php?go={}'.format(cavern_id)):
                    cavern_link = link
            cavern_link.click()
            
        except (ValueError, KeyError, AttributeError):
            raise BotParsingError


    def click_item(self):
        images = self.browser.find_elements_by_tag_name('img')
        srcs = [x.get_attribute('src') for x in images]
        items = []
        for no, src in enumerate(srcs):
            if 'drop_items' in src:
                items.append(images[no])
        if len(items) > 0:
            items[0].click()
            time.sleep(self.CLICK_ITEM_TIMEOUT)
            return True
        else:
            return False 


    def click_link(self, text):
        try:
            links = self.browser.find_elements_by_tag_name('a')
            link = links[[x.text for x in links].index(text)]
            link.click()
            time.sleep(self.CLICK_LINK_TIMEOUT)

        except (ValueError, KeyError):
            raise BotParsingError


    def click_object(self, name):
        try:
            images = self.browser.find_elements_by_tag_name('img')
            obj = images[[x.get_attribute('title') for x in images].index(name)]
            obj.click()
            time.sleep(self.CLICK_OBJECT_TIMEOUT)

        except (ValueError, KeyError):
            raise BotParsingError

    
    def get_hp(self):
        hp = self.browser.find_element_by_xpath('//*[@id="hp"]/div[2]/font/b')
        return tuple(map(int, hp.text.split('/')))
        

    def get_monsters(self):
        images = self.browser.find_elements_by_tag_name('img')
        monsters = []
        for image in images:
            width = image.get_attribute('width')
            height = image.get_attribute('height')
            if width == '100' and height == '160':
                monsters.append(image)
        return monsters


    def get_radio_buttons(self):
        attack_buttons = []
        defence_buttons = []
        
        inputs = self.browser.find_elements_by_tag_name('input')
        for button in inputs:
            if button.get_attribute('type') == 'radio':
                if button.get_attribute('name') == 'attack':
                    attack_buttons.append(button)
                if button.get_attribute('name') == 'defend':
                    defence_buttons.append(button)

        return attack_buttons, defence_buttons


    def screenshot(self, filename=None):
        now = time.localtime()
        if filename is None:
            filename = ('Screenshot_{0.tm_year}-{0.tm_mon:02}-{0.tm_mday:02}_'
                        '{0.tm_hour:02}{0.tm_min:02}{0.tm_sec:02}'
                        '.png'.format(now))
        print("Сохранён скриншот '" + filename + "'")
        self.browser.save_screenshot(filename)


    def select_main_frame(self):
        try:
            frames = self.browser.find_elements_by_tag_name('frame')
            main_frame = frames[[frame.get_attribute('name')
                                 for frame in frames].index('main')]
            self.browser.switch_to.frame(main_frame)
        except (ValueError, KeyError):
            raise BotParsingError        


class Bot:

    def __init__(self, username, password, engine):
        self.engine = engine
        self.engine.authorization(username, password)
        self.engine.select_main_frame()


    # A1. Получить задание
    def get_task(self, cavern_name):
        self.engine.click_cavern(cavern_name)
         
        try:
            self.engine.click_button('Задания')
            self.engine.click_button('Получить задание')
        except BotParsingError:
            print("Заданий нет")

        self.engine.click_button('Вернуться')
        self.engine.click_link('Портал воспоминаний')


    # A2. Завершить задание
    # Не протестировано!
    def end_task(self):
        self.engine.click_cavern(cavern_name)
         
        try:
            self.engine.click_button('Задания')
            self.engine.click_button('Завершить задание')
        except BotParsingError:
            print("Награды нет")

        self.engine.click_button('Вернуться')
        self.engine.click_link('Портал воспоминаний')

            
    # A3. Начать прохождение
    def enter_cavern(self, cavern_name):
        self.engine.click_cavern(cavern_name)
        self.engine.click_button('Создать группу')
        self.engine.click_button('Начать')


    # B1. Перемещения и повороты
    for direction in Engine.DIRECTIONS:
        exec('def move_{0}(self): '
             'self.engine.click_direction_button("{0}")'.format(direction))
    del direction


    # B2. Поднять предметы
    def collect(self):
        while self.engine.click_item():
            pass


    # B3. Использовать объект
    def use_object(self, name):
        self.engine.click_object(name)


    # B4. Напасть на монстра
    def attack(self):
        monsters = self.engine.get_monsters()
        if len(monsters) > 0:
            print("Обнаружены монстры:")
            for no, monster in enumerate(monsters, 1):
                print("    {:2}. {}".format(no, monster.get_attribute('title')))

            monsters[0].click()
            self.engine.click_link('Напасть')
        else:
            print("Монстры не обнаружены!")


    # B5. Разговор с НПЦ
    # Не реализовано!
    def talk(self):
        return NotImplemented


    # B6. Надеть комплект вещей
    # Не реализовано!
    def wear(name):
        return NotImplemented


    # B7. Ждать восстановления здоровья
    def wait_for_regeneration(self):
        while True:
            current_hp, max_hp = self.engine.get_hp()
            if current_hp == max_hp:
                break
            self.move_refresh()
            time.sleep(10)


    # B8. Использовать эликсир/свиток
    # Не реализовано!
    def use_artefact(self, name):
        return NotImplemented


    # C1. Ударить
    def punch(self, attack=0, defence=0):
        attack_buttons, defence_buttons = self.engine.get_radio_buttons()
        attack_buttons[attack].click()
        defence_buttons[defence].click()
        self.engine.click_button('Вперед !!!')


    # C2. Использовать приём
    # Какой-то баг при нескольких приёмах
    def use_ability(self, *numbers):
        for number in numbers:
            self.engine.click_ability(number)


    # C3. Закончить бой
    def end_attack(self):
        self.engine.click_button('Вернуться')


    # C4. Провести бой
    def combat(self, attack=0, defence=0, *numbers):
        self.attack()
        while True:
            try:
                self.end_attack()
                break
            except BotParsingError:
                self.use_ability(numbers)
                self.punch(attack, defence)


    # D1. Ждать
    def wait(self, seconds):
        time.sleep(seconds)
