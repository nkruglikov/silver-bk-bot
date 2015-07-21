import selenium
import time

class Engine:

    CAVERNS = [
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
    URL = 'http://silver-bk.com'
    CLICK_BUTTON_TIMEOUT = 1
    CLICK_LINK_TIMEOUT = 1


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


    def click_button(self, value):
        try:
            inputs = self.browser.find_elements_by_tag_name('input')
            button = inputs[[x.get_attribute('value')
                                   for x in inputs].index(value)]
            button.click()
            time.sleep(self.CLICK_BUTTON_TIMEOUT)

        except (ValueError, KeyError):
            raise BotParsingError


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


    def click_link(text):
        try:
            links = self.browser.find_elements_by_tag_name('a')
            link = links[[x.text for x in links].index(text)]
            link.click()
            time.sleep(self.CLICK_LINK_TIMEOUT)

        except (ValueError, KeyError):
            raise BotParsingError


    def screenshot(self, filename=None):
        now = time.localtime()
        if filename is None:
            filename = ('Screenshot_{0.tm_year}-{0.tm_mon:02}-{0.tm_mday:02}_'
                        '{0.tm_hour:02}{0.tm_min:02}{0.tm_sec:02}'
                        '.png'.format(now))
        print("Saving screenshot '" + filename + "'")
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
        
