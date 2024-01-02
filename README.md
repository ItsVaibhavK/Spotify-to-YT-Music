# PREFACE
I know I am not the first to decide to migrate my music from streaming platform A to streaming platform B, and come up against the daunting challenge of...<br>"Well, I have a LOT of songs in my playlists. How am I going to sit down and manually select and save songs on the new platform? That'll take me forever!"<br>Let me walk you through why the thought popped up in my head, and how I ultimately decided to tackle this challenge.

I already had YouTube Premium, though I wasn't really using YT Music. I had been a Spotify Premium customer for a **LONG** time. Then, one day, Spotify decided to do something<br>to really piss me off. They played me an advertisement. *Even though I was PAYING for Spotify Premium.*<br>There I was, driving along, listening to my tunes, when my music gets interrupted for an **ADVERTISEMENT** for **SPOTIFY WRAPPED.** I did not like that one bit.<br>That's when I decided I would finally make the switch to YT Music, and say goodbye to using Spotify forever.

Plus, I perceived a lot more benefits in using YouTube:
- By paying for YouTube Premium, not only was I getting ad-free YouTube access, but also a whole another app to listen to music and podcasts.
- In my experience, YouTube's algorithm was just better. I don't know how they do it. But every single new artist that I have ever loved, I discovered on YouTube<br>through their recommendations. I never found that on Spotify. In fact, Spotify did not seem to know how to even give me good recommendations.

My mind was made up. I was gonna make the switch. And with my past year spent learning programming, I was going to use Python to achieve my goal.<br>And wouldn't you know it, there were libraries to help on BOTH sides:
- [spotipy](https://spotipy.readthedocs.io/en/2.22.1/)
- [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/index.html)

But navigating these was not very easy in the beginning. Ultimately though, it worked well enough for me to consider the migration a success,<br>and this motivated me to put this project out there. I will try my best to explain all the hoops I had to jump through, and the difficulties I faced, so that this may hopefully help anyone else interested in doing the same. Maybe more experienced programmers could help improve upon what I've done.

# CREATING A SPOTIFY APP
The very first thing required for this project is to set up a Spotify App on [Spotify for Developers](https://developer.spotify.com/). The instructions to do the same [are available here](https://developer.spotify.com/documentation/web-api/concepts/apps).
- Log in with your Spotify credentials
- Click on *Create an App*
- Add a name, a description, and a redirect URI
- Since I was making this program for personal use, I just used the same redirect URI mentioned in the example of the documentation: `http://localhost:8080`
- Accept the terms, and click on *Create*

Once you've got to the app overview page, the main data required to authorise [spotipy](https://spotipy.readthedocs.io/en/2.22.1/) is the *client ID* and *client secret*.

# SETTING UP A VIRTUAL ENVIRONMENT
Observing best practices, and because of the sensitive credentials involved, I highly recommend setting up a virtual environment.<br>Here are the terminal commands I ran (I use VSCode/Windows):
1. `python3 -m venv DESIRED-NAME-OF-THE-FOLDER`
2. `source NAME-OF-THE-FOLDER/bin/activate`

# AUTHORISING SPOTIPY
Now, we set up our Spotify App credentials for [spotipy](https://spotipy.readthedocs.io/en/2.22.1/) with the following terminal commands:
- `export SPOTIPY_CLIENT_ID=PASTE YOUR APP CLIENT ID HERE`
- `export SPOTIPY_CLIENT_SECRET=PASTE YOUR APP CLIENT SECRET HERE`
- `export SPOTIPY_REDIRECT_URI=PASTE YOUR REDIRECT URI HERE`

# AUTHORISING YTMUSICAPI
Authorising [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/index.html) was a little more complex (for me, at least, going by the documentation) to get it working right. I ultimately managed to make it work<br>by following the instructions for [OAuth authentication](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html).

*Note: I had to perform the OAuth authentication steps twice, the first time for when I was migrating my user-created playlist in `user_playlist.py`,<br>and the second time for when I was migrating Spotify's platform-generated "Liked Songs" playlist in `liked_music_playlist.py`*

Following the steps for [OAuth authentication](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html) will create an `oauth.json` file in your current directory that can be used to authorise [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/index.html).

# EXECUTION
*Note: It should be obvious, but I would still like to point out that you must be logged in to your Spotify and YT Music accounts on your device while running these programs.*

### USER-CREATED PLAYLIST
The file `user_playlist.py` contains the logic for migrating a user-created Spotify playlist (a Spotify playlist that has a playlist ID, which the "Liked Songs" playlist does not have)<br>to a new YT Music playlist that will be created by this program.

The code is quite straightforward, I'll point out the logic as best as I can:
1. The program consists of a `main()` block and a custom function called `playlist()`
2. `print()` statements exist at certain points so that the execution is easier to follow/debug
3. The custom function `playlist()` takes a Spotify playlist ID as a parameter
4. Spotify only returns 100 items from a playlist at a time (at the time of writing this program), so a playlist that is longer than 100 items<br>has to be iterated through at steps of 100 items
5. The end of a Spotify playlist is indicated by the key:value pair `next:None` for the last item in the playlist, *hence the conditional if statement to end the for loop*
```
if response["next"] is None:
    print("Spotify playlist loaded")
    return
```
6. The results obtained from the above operation are stored in `items = list(playlist("YOUR PLAYLIST ID"))`
7. A new playlist is created on YT Music using `yt_playlist_id = yt_client.create_playlist("PLAYLIST NAME", "PLAYLIST DESCRIPTION")`
8. Each "item" in YT Music (a song, video) is identified by a unique "video ID"
9. An empty list `video_ids = []` is created to store the video IDs that will be extracted in the following steps
10. For each result obtained from Spotify, we extract the relevant information (song title, album name, artist(s) name(s)) and create a query string
11. The query string is then passed to YT Music, and a search is performed using `yt_response = yt_client.search(query)`
12. On YT Music, usually the first result is an exact match *if the song exists on the platform*
13. If the song does not exist on YT Music, only then will the top result be either a cover of the song by another artist(s),<br>or a live performance **video** of the song by the actual artist(s)
14. Points 12 and 13 work as follows:
```
if (
    result["resultType"] == "song"
    or result["resultType"] == "video"
    and result["title"] == title
):
    video_ids.append(result["videoId"])
    break
```
15. If a matching result is found, the video ID of that result is added to the empty list that was created in point number 9
16. If a matching result is not found, a message is printed out to the terminal:
```
print(f"{title} by {artists} not found.")
```
17. Once all the items from the list (from point number 6) have been iterated through and the corresponding video IDs have been obtained<br>(or not, if the song does not exist on YT Music), the matching results are then added into the YT Music playlist that was created in point number 7:
```
for video_id in video_ids:
    yt_client.add_playlist_items(yt_playlist_id, [video_id])
    print("Populating YouTube playlist")
```

And that's how it's done! In my user-created Spotify playlist, I had 56 songs that I was currently listening to on loop, and it found all 56 exact matches on YT Music,<br>including songs that had titles in foreign languages. I was *shocked.*

### SPOTIFY'S PLATFORM-CREATED "LIKED SONGS" PLAYLIST
The file `liked_music_playlist.py` contains the logic for migrating the Spotify-created "Liked Songs" playlist into a new playlist on YT Music that will be created by the program. The code, for the most part, is exactly the same as the previous program, so I'll mainly only point out the differences here:
1. The authorisation flow is a bit different, in that, a different module is imported `from spotipy.oauth2 import SpotifyOAuth` and the scope **has to be declared as follows**: `scope = "user-library-read"` Otherwise, Spotify will not allow access to the "Liked Songs" playlist
2. There is no Spotify playlist ID for the "Liked Songs" playlist, instead, it is accessed using `spotify_client.current_user_saved_tracks()`
3. Increments of 100 items as per point number 4 in the above section did not work, steps of 50 items at a time, however, worked better

That's about all the differences in the two programs. In my Spotify "Liked Songs" playlist, I had somewhere around 860 songs. The program found 856 songs, missing out on 4 songs that weren't on YT Music at all as audio or video, and it only got 1 song *wrong*.

That's more success than I had even hoped for. I would have been happy with a 50% success rate, ironically.

# ISSUES I FACED
The first glaring issue is a personal/subjective one. None of the documentation for [spotipy](https://spotipy.readthedocs.io/en/2.22.1/) or [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/index.html) is beginner-friendly, and some of the instructions just don't produce results or offer any helpful error messages. I lost a lot of time in trying to iron out these problems. This, however, may not be an issue for the more experienced programmer.

The real (perhaps more annoying) issue was the speed. Often times, [spotipy](https://spotipy.readthedocs.io/en/2.22.1/) would just hang in what seemed like endless "sleep-retry-after" cycles. And there was *no indication* as to what was going on, which is why I added in the `print()` statements at various points of the programs to know where they were in their execution.

What worked best when such an issue arose was to try again after a gap of 2-3 hours, and to be *very patient* with the time [spotipy](https://spotipy.readthedocs.io/en/2.22.1/) took to execute its calls.

# CREDITS & CONCLUSION
Both programs, in the end, helped me reach my goal with a success rate of 99% (and change). In my eyes, this was an absolute win. Can you imagine how long it would have taken<br>to manually add 800+ songs from my Spotify "Liked Songs" playlist to a playlist on YT Music? I shudder at the thought. I learnt a lot along the way, and this was way more fun<br>than I expected it to be. Since I made the move, I ended **and** deleted my Spotify account (and the Spotify App that I had created to run these programs).<br>I've exclusively been using YT Music all this while to listen to/discover music and podcasts, and there's no complaints from me so far.

To create these programs, I utilized a whole bunch of resources and documentation, but I mainly want to thank somebody I found on YouTube.<br>This person had a livestream recording up from a year ago, and the meat of the logic of my programs is derived from them.

Here's the [link to their video](https://www.youtube.com/watch?v=DTiXJK72XvE&t=4912s). Thank you, stranger, for helping me along on my programming journey! I hope I help someone else along, even with a little project like this one!
