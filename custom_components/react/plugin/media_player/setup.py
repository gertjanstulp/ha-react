import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup
from custom_components.react.plugin.media_player.api import MediaPlayerApi, MediaPlayerConfig
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.plugin.media_player.const import (
    ATTR_MEDIA_PLAYER_PROVIDER, 
    ATTR_TTS_PROVIDER
)
from custom_components.react.plugin.media_player.input.state_change_input_block import MediaPlayerStateChangeInputBlock
from custom_components.react.plugin.media_player.output.speek_output_block import MediaPlayerSpeekOutputBlock
from custom_components.react.plugin.media_player.output.play_favorite_output_block import MediaPlayerPlayFavoriteOutputBlock


MEDIA_PLAYER_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_MEDIA_PLAYER_PROVIDER) : cv.string,
    vol.Optional(ATTR_TTS_PROVIDER) : cv.string,
})


class Setup(PluginSetup[MediaPlayerConfig]):
    def __init__(self) -> None:
        super().__init__(MEDIA_PLAYER_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> MediaPlayerConfig:
        return MediaPlayerConfig(raw_config)


    def setup_api(self, setup: ApiSetupCallback):
        setup(MediaPlayerApi)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(MediaPlayerStateChangeInputBlock)
    

    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(
            [
                MediaPlayerPlayFavoriteOutputBlock,
                MediaPlayerSpeekOutputBlock,
            ],
        )
