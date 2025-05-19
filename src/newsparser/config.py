from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.txt")

EXTRA_FILES_FOLDER = os.getenv("EXTRA_FILES_FOLDER", "")

if EXTRA_FILES_FOLDER:
    os.makedirs(EXTRA_FILES_FOLDER, exist_ok=True)

def get_chrome_options():
    """
    Возвращает настроенный объект Chrome Options
    """
    options = Options()
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.page_load_strategy = 'eager'
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.cookies": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.media_stream": 2,
    }
    options.add_experimental_option("prefs", prefs)
    return options
