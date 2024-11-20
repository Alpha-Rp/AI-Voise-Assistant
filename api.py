import enum
from typing import Annotated
from livekit.agents import llm
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger("temperature-control")
logger.setLevel(logging.INFO)

class Zone(enum.Enum):
    LIVING_ROOM = "living_room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    OFFICE = "office"

class AssistantFnc(llm.FunctionContext):
    def __init__(self) -> None:
        super().__init__()

        self._temperature = {
            Zone.LIVING_ROOM: 22,
            Zone.BEDROOM: 20,
            Zone.KITCHEN: 24,
            Zone.BATHROOM: 23,
            Zone.OFFICE: 21,
        }

        # Set up your Spotify API credentials
        self.SPOTIPY_CLIENT_ID = 'your_client_id'  # Replace with your actual Client ID
        self.SPOTIPY_CLIENT_SECRET = 'ea33f8859d804842bdb8875facca3bc3'  # Your API key
        self.SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback/'  # Change to your registered redirect URI

        # Authenticate with Spotify
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.SPOTIPY_CLIENT_ID,
                                                           client_secret=self.SPOTIPY_CLIENT_SECRET,
                                                           redirect_uri=self.SPOTIPY_REDIRECT_URI,
                                                           scope='user-library-read user-read-playback-state user-modify-playback-state'))

    @llm.ai_callable(description="get the temperature in a specific room")
    def get_temperature(
        self, zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")]
    ):
        logger.info("get temp - zone %s", zone)
        temp = self._temperature[Zone(zone)]
        return f"The temperature in the {zone} is {temp}C"

    @llm.ai_callable(description="set the temperature in a specific room")
    def set_temperature(
        self,
        zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")],
        temp: Annotated[int, llm.TypeInfo(description="The temperature to set")],
    ):
        logger.info("set temp - zone %s, temp: %s", zone, temp)
        self._temperature[Zone(zone)] = temp
        return f"The temperature in the {zone} is now {temp}C"

    @llm.ai_callable(description="get the current temperature in a specific room")
    def get_current_temperature(self, zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")]):
        logger.info("Getting current temperature for zone: %s", zone)
        temp = self._temperature[zone]
        return f"The current temperature in the {zone.value} is {temp}C."

    @llm.ai_callable(description="play a specific track on Spotify")
    def play_specific_track(self, track_name: Annotated[str, llm.TypeInfo(description="The name of the track to play")]):
        logger.info("Playing track: %s", track_name)
        track = self.search_track(track_name)
        if track:
            self.play_track(track['uri'])
            return f"Now playing {track['name']} by {track['artists'][0]['name']}."
        return "Track not found."

    @llm.ai_callable(description="pause the current track on Spotify")
    def pause_current_track(self):
        logger.info("Pausing current track")
        self.pause_playback()
        return "Playback paused."

    @llm.ai_callable(description="skip to the next track on Spotify")
    def skip_to_next_track(self):
        logger.info("Skipping to next track")
        self.skip_to_next()
        return "Skipped to the next track."

    def search_track(self, track_name):
        results = self.sp.search(q=track_name, type='track')
        return results['tracks']['items'][0] if results['tracks']['items'] else None

    def play_track(self, track_uri):
        self.sp.start_playback(uris=[track_uri])

    def pause_playback(self):
        self.sp.pause_playback()

    def skip_to_next(self):
        self.sp.next_track()