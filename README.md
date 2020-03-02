# A-RTFC
A-RTFC is a fork of [Deckmaster by Fugiman](https://github.com/Fugiman/deckmaster). Fugiman had a lot of things inside the code that made it difficult to develop for and/or deploy your own version. This cleaned up a significant amount and includes some scripts to make it easy to deploy your own version.

# Instructions

There are 3 parts to this: the server, the client, and the actual extension code we upload to twitch.

## Requirements
- Node
- Yarn
- Python3 with Requests Library
- Some sort of Bash Interpreter

## Instructions
Included is a `setup_vars_example.ini`. Rename this to `setup_vars.ini`. The script `setup-build.py` will use this file to insert the appropriate information into all the files in the project. It will replace all instances of the key (designated by <>) with the value assigned to it in the .ini file. Our first job is to get the information needed for it. 

First we will create the Twitch extension at dev.twitch.tv. When you create the extension, you will need to give it a name. Then, it will ask what type of an extension it is. Select 'Video - Fullscreen' and 'Mobile'. Rest of the information is optional. Click 'Create Extension Version' In the upper right is your Client ID. Copy and Paste that into the `client_id` value in your `setup_vars.ini` file. 

Just to the right of that is "Extension Settings". This will bring you to where you get your keys. Generate the Twitch API Secret. Copy Paste that value into the `client_secret` value in the ini file. NOTE: This is irrecoverable. If you somehow lose it, you cannot get it back and must generate a new one. 

A little further down there is the Extension Client Configuration. There will be a secret already there. Just reveal it. It should end with a '='. Paste this into the `ext_secret` value in the ini file. Rest of the stuff is what you want to fill in for your config.

- `hostname`: The hostname of the server.
- `port`: The port the server will listen on.
- `server_url`: How the client will find the server. Note that if the port is not a normal port, you may need to specify it.
- `websocket_url`: The server maintains a websocket with clients. It should look like the `server_url` but starts with "wss://" instead of "https://".
- `download_link`: A link to where they can download the client. This shows up if a user tries to use the config from the Twitch dash.
- `extension_url`: A link to the actual extension in Twitch. It will have the extension client_id at the end.
- `logo_url`: This is the URL for the little logo on the side. You can probably just use Fugi's at https://deckmaster.fugi.io/logo.png for now.

Once all that is filled in, we have 2 python scripts and a bash script to run. Both require Python3 and `scryfall_card_gen.py` requires the request library. A `requirements.txt` is provided if you wish to set up a python virtual environment instead of using a global one. First, run the Python scripts `scryfall_card_gen.py` and then `setup-build.py`. NOTE: `setup-build.py` will alter all the files. If there is an error in the .ini file, things will get messed up. Just use `git reset --hard` if needed to go back to when I gave it to you. `scryfall_card_gen.py` will update all the card lists and put them in the api folder and put a card list in the client folder. The client folder card list is for if the Twitch user wishes to use draft voting. NOTE: Draft voting has not been tested, however, I don't believe I altered anything that would make it fail.

Once that is done, it's time to run the build script, `build.sh`. You may need to set it as an executable. This will do all the hard work and go into each folder and build it. It will put everything in a dist folder. 

Now, we have a couple other things to do on the Twitch page to get the overlay to work. In the extension settings, where we last left off, there is a field for "OAuth Redirect URL". Use the server url value in the setup_vars.ini file for this but make sure to add `/login` to the end of it. It must equal exactly that. If it isn't exact, then it won't work. Then click on the name of your extension up top left, and then click 'manage' for your extension in the list. Then, click the files tab. In your dist folder, there should be a compressed file called 'Twitch.zip'. Upload this. Then, go to "Asset Hosting". Fill in the following textboxes as follows:
- Video - Fullscreen Viewer Path: `overlay/index.html`
- Mobile Path: `mobile/index.html`
- Config Path: `config/index.html`
- Live Config Path: Leave Blank

Last thing we need to do is turn the extension on. Go back to status and press 'Move to Local Test'. Last thing we need to do is install it. Near the bottom there is 'View on Twitch and Install'. This will take you to the Extension page on Twitch where you install it. Make sure it's overlay 1.

Now make sure the server is running. To turn it on, go to the api folder and run `node main.js`. It should tell you the hostname and port it's running on. Last thing we need to do now is fire up the client. Make sure ARENA_LOG_PATH is set first. In the `dist` folder there is an appimage that you can run.

## Notes
The Extension will not be published yet and anyone who wishes to use it needs to be whitelisted which you do under the 'Access' Tab. There is apparently some sort of review process that needs to be done and I'm unfamiliar with that.

Under the 'Version Details' tab is where you upload all the stuff like summary and description as well as the Logo and a few other things. This stuff is what appears in the Extension store.

This will not build an .exe for Windows. You will need to build it on a Windows machine or in a container with Wine. I don't know how to do the container way as I just used Windows to build the .exe. However, instructions are a little different as Windows cannot run bash scripts. You will need to go into the overlay folder in a cmd terminal and use `yarn install`, then go into the client folder, `yarn install` and then `yarn build`. Note that you will need to install Node and yarn for this to work. This should create a .exe file under `client/build/`. This can be distributed.
