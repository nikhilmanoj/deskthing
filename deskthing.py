import RPi.GPIO as GPIO
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set up Spotify OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="XXXXXXXXXXXXXXXXXXX",
    client_secret="XXXXXXXXXXXXXXXXXXXX",
    redirect_uri="http://localhost:8000/callback",
    scope="user-read-playback-state,user-modify-playback-state,playlist-read-private"
))

# Set up GPIO pins for rotary encoder
Enc_A = 20
Enc_B = 21

# Set up GPIO pins for Spotify control
PLAY_PAUSE_PIN = 23
NEXT_TRACK_PIN = 24
PREVIOUS_TRACK_PIN = 25
TOGGLE_PLAYLIST_PIN = 12

# Initialize variables
counter = 50  # Start volume at 50%
current_playlist_index = 0
current_track = None

# Rotary encoder variables
counter_max = 100
counter_last_state = 0
counter_last_result = 0

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Enc_A, GPIO.IN)
    GPIO.setup(Enc_B, GPIO.IN)
    GPIO.setup(PLAY_PAUSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(NEXT_TRACK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PREVIOUS_TRACK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TOGGLE_PLAYLIST_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Add event detection for rotary encoder and Spotify control buttons
    GPIO.add_event_detect(Enc_A, GPIO.BOTH, callback=rotation_decode, bouncetime=10)
    GPIO.add_event_detect(PLAY_PAUSE_PIN, GPIO.RISING, callback=toggle_play_pause, bouncetime=1000)
    GPIO.add_event_detect(NEXT_TRACK_PIN, GPIO.RISING, callback=skip_to_next_track, bouncetime=1000)
    GPIO.add_event_detect(PREVIOUS_TRACK_PIN, GPIO.RISING, callback=skip_to_previous_track, bouncetime=1000)
    GPIO.add_event_detect(TOGGLE_PLAYLIST_PIN, GPIO.RISING, callback=toggle_user_playlist, bouncetime=1000)

def rotation_decode(channel):
    global counter, counter_last_state, counter_last_result
    MSB = GPIO.input(Enc_A)
    LSB = GPIO.input(Enc_B)

    # Convert the rotary encoder state to decimal
    rotary_state = (MSB << 1) | LSB

    # Determine the direction of rotation
    direction = (rotary_state - counter_last_state) % 4

    if direction == 1:
        counter += 1
    elif direction == 3:
        counter -= 1

    # Limit the counter within the valid range
    counter = max(0, min(counter_max, counter))

    if counter != counter_last_result:
        print("Direction ->", direction, "Counter ->", counter)
        set_volume(counter)

    # Update the last state and result
    counter_last_state = rotary_state
    counter_last_result = counter

def toggle_play_pause(channel):
    global current_track
    try:
        current_track = sp.current_playback()
        if current_track and 'is_playing' in current_track:
            if current_track['is_playing']:
                sp.pause_playback(device_id=current_track['device']['id'])
                print("Playback paused.")
            else:
                sp.start_playback(device_id=current_track['device']['id'])
                print("Playback started.")
        else:
            print("No track is currently playing. Starting the first track from your library.")
            start_first_track()
    except spotipy.SpotifyException as e:
        print(f"Spotify API Error: {e}")
        if e.http_status == 403 and e.code == -1:
            print("Player command failed: Restriction violated.")

def skip_to_next_track(channel):
    global current_track
    try:
        current_track = sp.current_playback()
        sp.next_track(device_id=current_track['device']['id'])
        print("Skipping to the next track.")
    except spotipy.SpotifyException as e:
        print(f"Spotify API Error: {e}")
        if e.http_status == 403 and e.code == -1:
            print("Player command failed: Restriction violated.")

def skip_to_previous_track(channel):
    global current_track
    try:
        current_track = sp.current_playback()
        sp.previous_track(device_id=current_track['device']['id'])
        print("Skipping to the previous track.")
    except spotipy.SpotifyException as e:
        print(f"Spotify API Error: {e}")
        if e.http_status == 403 and e.code == -1:
            print("Player command failed: Restriction violated.")

def toggle_user_playlist(channel):
    global current_track
    try:
        playlists = sp.current_user_playlists()
        if playlists['items']:
            current_track = sp.current_playback()
            current_playlist_index = (current_playlist_index + 1) % len(playlists['items'])
            selected_playlist = playlists['items'][current_playlist_index]
            print(f"Toggle user playlist. Currently playing playlist: {selected_playlist['name']}")
            start_first_track_from_playlist(selected_playlist['id'])
        else:
            print("No playlists found.")
    except spotipy.SpotifyException as e:
        print(f"Spotify API Error: {e}")
        if e.http_status == 403 and e.code == -1:
            print("Player command failed: Restriction violated.")

def start_first_track_from_playlist(playlist_id):
    global current_track
    try:
        current_track = sp.current_playback()
        tracks = sp.playlist_tracks(playlist_id)['items']
        if tracks:
            first_track_uri = tracks[0]['track']['uri']
            sp.start_playback(device_id=current_track['device']['id'], uris=[first_track_uri])
            print("Playback started with the first track from the playlist.")
        else:
            print("No tracks found in the playlist.")
    except spotipy.SpotifyException as e:
        print(f"Spotify API Error: {e}")
        if e.http_status == 403 and e.code == -1:
            print("Player command failed: Restriction violated.")

def set_volume(volume_percent):
    global current_track
    # Use the spotipy library to set the Spotify volume
    try:
        sp.volume(volume_percent)
        print(f"Set Volume to: {volume_percent}")
    except spotipy.SpotifyException as e:
        print(f"Spotify API Error: {e}")

def start_first_track():
    global current_track
    try:
        current_track = sp.current_playback()
        if current_track and 'is_playing' in current_track:
            print("A track is already playing.")
        else:
            liked_songs = sp.current_user_saved_tracks()
            if liked_songs['items']:
                first_track_uri = liked_songs['items'][0]['track']['uri']
                sp.start_playback(device_id=current_track['device']['id'],
