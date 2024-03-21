Raspberry Pi Spotify Remote Controller

This is an initial version of a desktop remote music controller for Spotify that runs on Raspberry Pi. It's an early prototype intended as an open-source project. The code allows you to control basic Spotify playback functions such as play/pause, skip to next/previous track, adjust volume, and toggle playlists using GPIO pins on the Raspberry Pi.

Installation

To use this remote music controller, follow these steps:

1. Clone this repository to your Raspberry Pi.
2. Install the required dependencies:

   pip install RPi.GPIO spotipy
   
3. Obtain Spotify API credentials by registering your application on the Spotify Developer Dashboard.
4. Update the client_id and client_secret in the code with your Spotify API credentials.
5. Run the Python script:

   python spotify_remote.py

Usage

- Rotary Encoder: Rotate to adjust the volume.
- Play/Pause Button: Press to toggle play/pause.
- Next Track Button: Press to skip to the next track.
- Previous Track Button: Press to skip to the previous track.
- Toggle Playlist Button: Press to cycle through your playlists and start playing the first track of the selected playlist.

GPIO Pins Configuration

- Rotary Encoder:
  - Encoder A: GPIO 20
  - Encoder B: GPIO 21

- Spotify Control:
  - Play/Pause Button: GPIO 23
  - Next Track Button: GPIO 24
  - Previous Track Button: GPIO 25
  - Toggle Playlist Button: GPIO 12

Contributions

Contributions to this project are welcome. Feel free to fork the repository, make improvements, and submit pull requests.

License

This project is licensed under the MIT License.
