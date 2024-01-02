import itertools
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import ytmusicapi

auth_manager = SpotifyClientCredentials()
spotify_client = spotipy.Spotify(auth_manager=auth_manager)
yt_client = ytmusicapi.YTMusic("oauth.json")


def main():
    # insert Spotify playlist ID inside the quotation marks
    # list of every song and its details from your Spotify playlist, see "playlist" function below "main"
    items = list(playlist("YOUR PLAYLIST ID"))

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


def playlist(spotify_playlist_id):
    print("Loading Spotify playlist")
    '''
        Spotify allows you to load only 100 songs at a time (at the time of writing this program)
        so we have to go through the playlist in increments of 100 items
    '''
    for offset in itertools.count(step=100):
        response = spotify_client.playlist_items(
            spotify_playlist_id, offset=offset, limit=100
        )
        print("Loading...")
        for item in response["items"]:
            yield item
        '''
            Spotify signals the end of a playlist by setting the value of "next" for the last item
            to be equal to "None"
        '''
        if response["next"] is None:
            print("Spotify playlist loaded")
            return


if __name__ == "__main__":
    main()
