![Alt text](static/css/images/splash.jpg?raw=true "Title")

# VRNetzer Backend

This is a flask server that provides the network data to the UnrealEngine VRNetzer VR Clients

# VRNetzer VR-Module 

Please find the build of the newest VRNetzer VR Module <a style="font-size:14px" href="https://ucloud.univie.ac.at/index.php/s/kUNbOhrn8Bsl50d" target="_blank">here</a>.
To run the Module download the folder and execute the .exe file. 

## INSTALLATION

1. run backend

   - install python 3.9 plus
   - windows: run `Buildandrun.ps1` in console
   - linux: run `linux_buildandrun.sh` in console
   - mac: run `linux_buildandrun.sh` in console

   If all dependencies installed correctly, the console should show </br>
   `The server is now running at 127.0.0.1:5000`

   As on mac port 5000 is already occupied by the systems control center, on mac the server will run on port 3000 (instead of 5000).

2. upload data and create new project

   - open a browser (Chrome or Firefox) and go to [127.0.0.1:5000/upload](http://127.0.0.1:5000/upload) / [127.0.0.1:3000/upload](http://127.0.0.1:3000/upload)(mac)
   - make sure "create new project" is checked and assign a name
   - choose a layout file from "static/examplefiles" (or more) or use your own
   - pick a link file from "static/examplefiles" (same name as above) or use your own
   - click upload

   After a success message was shown, the uploader has now created a new folder in "static/projects/yourprojectname" containing all the data in the VRNetzer format.

3. use the WebGL preview to have a look at your project without having to use VR hardware

   - go to [127.0.0.1:5000/preview](http://127.0.0.1:5000/preview) / [127.0.0.1:3000/preview](http://127.0.0.1:3000/preview)(mac)
   - select your project from the dropdown

4. run the VR
   you need:
   - a VR ready windows computer
   - a SteamVR compatible headset
   - SteamVR installed
   - download the VRNetzer executable
   - open "VRNetzer/Colab/Content/data/config.txt and make sure it contains the adress the VRNetzer backend is running at
   - run the backend
   - run VRnetzer.exe
   - enter a username (optional)
   - choose robot if you want to run in desktop mode (good idea for a dedicated server as it is more performant) OR VR to run in vr mode
   - the first player is the host so choose "HOST SESSION"
   - the following players choose "JOIN SESSION"

## DOCUMENTATION

Once the flask server is running, go to [127.0.0.1:5000/doku](http://127.0.0.1:5000/doku) / [127.0.0.1:3000/doku](http://127.0.0.1:3000/doku)(mac) to learn more about the VRNetzer framework

<details>
  <summary><h3> VRNetzer Dataformat</h3></summary>
    
The VRNetzer acts as a multiplayer gameserver for one or more VR clients.
Its purpose is to serve the connected players with big network datasets - as quickly as possible.
That is the reason why most properties are stored (and transmitted over the network) as images.

Every folder in "static/projects/ contains 3 JSON files (check out the file dataframeTemplate.json for the exact structure)
as well as 5 subfolders containing textures

- static/projects/projectname/
   - nodes.json
   - links.json
   - pfile.json
   - pdata.json
  - layouts
      - layout01XYZ.bmp
      - layout02XYZ.bmp
  - layoutsl
      - layoutl01XYZ.bmp
      - layoutl02XYZ.bmp
  - layoutsRGB
      - layout01RGB.png
      - layout02RGB.png
  - links
      - links.bmp
  - linksRGB
      - linksRGB.png

layouts + layoutsl -> Node Positions

this needs a little explaining:
Think of a texture as a dataset of the following format: [[R,G,B],[R,G,B],[R,G,B],..] 
where every [R,G,B] is a pixel.
This can be used to store a location (X->R Y->G Z->B) per pixel.
Because a .bmp only has 8 bit depth we need a second texture to get a resolution of 65536 per axis. this is where "layoutsl" comes into play.
NOTE: node positions need to be in a 0 - 1 range (!), the conversion works like this:

floor(x _ 256) -> layouts
floor(x _ 65536 % 256) -> layoutsl

This means, that the available space is not unlimited, so when nodes are closer than 1/65536 units they will snap together.

</details>

<details>
<summary><h3>HOW TO MAKE YOUR OWN USER INTERFACE</h3></summary>
The User Interfaces for the VRNetzer are realized with html and js and are rendered in the UnrealEngine in-game webbrowser, which is Chromium. Data is passed between the flask server and the html clients in JSON format. The html pages also act as a middleman between the UnrealEngine VR Module and the flask server.
Here is a series of examples that explain in detail how to create your own user interfaces.
(you have to run the flask server locally to see those pages)

go to [127.0.0.1:5000/doku](http://127.0.0.1:5000/doku) / [127.0.0.1:3000/doku](http://127.0.0.1:3000/doku)(mac)

</details>


<br><br>

