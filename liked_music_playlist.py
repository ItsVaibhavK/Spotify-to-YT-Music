import itertools
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import ytmusicapi

# important to set this scope, otherwise Spotify does not allow access to the "Liked Songs" playlist
scope = "user-library-read"
spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

yt_client = ytmusicapi.YTMusic("oauth.json")


def main():
    # no Spotify playlist ID involved for the "Liked Songs" playlist
    items = list(playlist())

    # insert the desired YT Music playlist name and description inside the quotation marks
    yt_playlist_id = yt_client.create_playlist("PLAYLIST NAME", "PLAYLIST DESCRIPTION")
    print("YouTube playlist created")
    # empty list to store YT Music "Video IDs" from the search results
    video_ids = []

    for item in items:
        # song title
        title = item["track"]["name"]
        # name of the album the song is a part of
        album = item["track"]["album"]["name"]
        # name of the artist(s)
        artists = "".join(
            [a["name"] for a in item["track"]["artists"] if a["type"] == "artist"]
        )
        # constructed query string that is to be searched on YT Music
        query = f"{title} {album} {artists}"
        # run the search on YT Music
        yt_response = yt_client.search(query)
        '''
            Usually, on YT Music, the first result is the exact match we are looking for, otherwise
            the song is probably not available on YT Music, in which case we accept a video of the same,
            like a live performance of the song, for example
        '''
        for result in yt_response:
            if (
                result["resultType"] == "song"
                or result["resultType"] == "video"
                and result["title"] == title
            ):
                video_ids.append(result["videoId"])
                break
        else:
            print(f"{title} by {artists} not found.")

    for video_id in video_ids:
        yt_client.add_playlist_items(yt_playlist_id, [video_id])
        print("Populating YouTube playlist")
    
    print("Migration complete")


def playlist():
    print("Loading Spotify \"Liked Songs\" playlist")
    # a smaller step count worked better for some reason unlike the other program, where a step of 100 worked
    for offset in itertools.count(step=50):
        response = spotify_client.current_user_saved_tracks(
            offset=offset, limit=50
        )
        print("Loading...")
        for item in response["items"]:
            yield item
        '''
            Spotify signals the end of a playlist by setting the value of "next" for the last item
            to be equal to "None"
        '''
        if response["next"] is None:
            print("Spotify \"Liked Songs\" playlist loaded")
            return


if __name__ == "__main__":
    main()
