import json
import requests

class SpotifyClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://api.spotify.com/v1'

    def _auth_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_my_user_id(self):
        response = requests.get(
            f'{self.base_url}/me', headers=self._auth_headers())

        if response.status_code == 200:
            user_data = response.json()
            return user_data["id"]
        else:
            print(f"Error: {response.status_code}")
            return None

    def get_user_playlists(self, user_id: str):
        playlists = []
        offset = 0
        limit = 50
        url = f'{self.base_url}/users/{user_id}/playlists?limit={limit}&offset={offset}'
        content = {"next": url}
        while len(playlists) < 500 and content['next']:
            response = requests.get(
                content['next'], headers=self._auth_headers())
            response.raise_for_status()
            content = response.json()
            for playlist in response.json()['items']:
                playlists.append(playlist)
        print(json.dumps(playlists, indent=4))
        return playlists

    def find_playlist(self, name: str, user_id: str):
        playlists = self.get_user_playlists(user_id)
        for playlist in playlists:
            if playlist['name'] == name:
                return playlist

        return None

    def create_playlist(self, user_id: str, name: str, public: bool):
        data = {
            'name': name,
            'public': public
        }
        print(data)
        response = requests.post(
            f'{self.base_url}/users/{user_id}/playlists', headers=self._auth_headers(), json=data)
        response.raise_for_status()

        return response.json()['id']

    def get_songs_from_playlist(self, playlist_id: str):
        response = requests.get(
            f'{self.base_url}/playlists/{playlist_id}/tracks', headers=self._auth_headers())
        response.raise_for_status()

        tracks = []
        for track in response.json()['items']:
            dct = {}
            dct['title'] = track['track']['name']
            dct['track_uri'] = track['track']['uri']
            dct['album_name'] = track['track']['album']['name']
            dct['artists'] = track['track']['artists']
            dct['duration_ms'] = track['track']['duration_ms']
            dct['explicit'] = track['track']['explicit']
            tracks.append(dct)

        return {"tracks": tracks}

    def add_songs_to_playlist(self, playlist_id: str, song_uris: list[str]):
        data = {
            'uris': song_uris
        }
        response = requests.post(
            f'{self.base_url}/playlists/{playlist_id}/tracks', headers=self._auth_headers(), json=data)
        response.raise_for_status()

    def remove_songs_from_playlist(self, playlist_id: str, track_uris: list[str]):
        data = {
            'tracks': [{'uri': uri} for uri in track_uris]
        }
        print(data)
        response = requests.delete(
            f'{self.base_url}/playlists/{playlist_id}/tracks', headers=self._auth_headers(), json=data)
        response.raise_for_status()

    def search_track(self, query: str, limit=10):
        params = {
            'q': query,
            'type': 'track',
            'limit': limit
        }
        response = requests.get(
            f'{self.base_url}/search', headers=self._auth_headers(), params=params)
        response.raise_for_status()
        return response.json()['tracks']['items']