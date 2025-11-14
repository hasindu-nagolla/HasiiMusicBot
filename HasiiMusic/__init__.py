from HasiiMusic.core.bot import MusicBotClient
from HasiiMusic.core.dir import StorageManager
from HasiiMusic.core.git import git
from HasiiMusic.core.userbot import Userbot
from HasiiMusic.misc import dbb, heroku
from HasiiMusic.logging import LOGGER

StorageManager()
git()
dbb()
heroku()

app = MusicBotClient()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()