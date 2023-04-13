import os
from gettext import translation
import locale

# Specifies the language to be used. The language is taken from the environment variable and defaults to 'en'.
language, country = locale.getdefaultlocale()
if language is None:
    language = "en"
print(language)

# Sets the path to the directory where the locale files are stored.
locales_path = os.path.join(os.getcwd(), 'locales')

# Create a translation object.
trans = translation(language, localedir=locales_path, languages=[language], fallback=False)
# Check if the translation object loaded the translation file successfully.
if trans is None:
    print("Translation file could not be loaded!")
else:
    # Import the gettext function (_function) from the translation object.
    _ = trans.gettext
    print(locales_path)
