import pytest

from src.exceptions import TrackNotFound
from src.definitions.definitions import FILES_DIR
from src.models import Action, File, ShazamTrack


def test_file():
    """Creates a normal File object"""

    file = File(Action.GDRIVE_UPLOAD,
                     file_title="random_song",
                     file_id="C2aks09k2as",
                     mime_type="audio/mpeg",
                     chat_id="8028940")

    assert file.get_file_location() == FILES_DIR + file.file_title


def test_shazam_track():
    """Creates a normal ShazamTrack object"""

    unserialized_track = {
        'track': {
            'title': 'Random Song Title',
            'subtitle': 'Song subtitle',
            'images': {
                'coverarthq': 'www.randomserver.org/picture1.jpg'
            },
            'hub': {
                'providers' : [
                    {
                        'caption': "song caption random",
                        'actions': [
                            {
                                'uri': "www.spotifydeeplinkexample.com"
                            }
                        ]
                    }
                ]
            }
        }
    }

    shazam_track = ShazamTrack(unserialized_track)
    assert shazam_track.track == unserialized_track['track']
    assert shazam_track.title == unserialized_track['track']['title']
    assert shazam_track.image == unserialized_track['track']['images']['coverarthq']
    assert shazam_track.subtitle == unserialized_track['track']['subtitle']
    assert shazam_track.first_provider['caption'] == unserialized_track['track']['hub']['providers'][0]['caption']
    assert shazam_track.first_provider['uri'] == unserialized_track['track']['hub']['providers'][0]['actions'][0]['uri']


def test_shazam_track_invalid():
    """Creates a normal ShazamTrack object but raises invalid key"""

    incomplete_unserialized_track = {
        'track': {
            'title': 'Random Song Title',
            'images': {
                'coverarthq': 'www.randomserver.org/picture1.jpg'
            },
        }
    }

    with pytest.raises(TrackNotFound):
        shazam_track = ShazamTrack(incomplete_unserialized_track)


