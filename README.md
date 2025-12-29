# RCON
A remote console flask web-app for minecraft servers

### Development
To run the development server enter `flask --app hello run` from the project root after installing all dependencies in `requirements.txt` by using `pip install -r requirements.txt`

When developing on this repo you'll need to create a `.env` file, there's a `.env.example` file that should look something like this:
```
MINECRAFT_SERVER_IP=
MINECRAFT_SERVER_RCON_PORT=
MINECRAFT_SERVER_QUERY_PORT=
```

Mine (when populated) looks like this:
```
MINECRAFT_SERVER_IP=10.0.0.150
MINECRAFT_SERVER_RCON_PORT=25566
MINECRAFT_SERVER_QUERY_PORT=25567
```
When setting these it's important to know the RCON AND QUERY ports of your minecraft server, and *not* the general access port for the server. By default minecraft (java edition), uses port 25565 for the game, so if you're using that, you've got the wrong port. You can find the rcon and query ports in the `server.properties` file under `rcon.port` and `query.port` variables.

To use the file simply copy the `.env.example` and rename it as `.env` and populate it with your server's details.
