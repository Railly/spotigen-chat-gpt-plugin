from pydantic import BaseModel

class TrackTitles(BaseModel):
    titles: list[str]

class TrackURIs(BaseModel):
    track_uris: list[str]

class Artist(BaseModel):
    name: str
    id: str
    uri: str
    href: str
    external_urls: dict[str, str]

class Track(BaseModel):
    title: str
    track_uri: str
    artists: list[Artist]
    duration_ms: int
    explicit: bool

class PlaylistTracksResponse(BaseModel):
    tracks: list[Track]
