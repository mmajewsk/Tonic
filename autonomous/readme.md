# TonicAutonomous.

![](https://imgur.com/oA3ERWN.gif)

This repository contains a code for navigation and autonomous driving of the [Tonic](https://github.com/mmajewsk/Tonic) project.

## Step by step
So how to use this. This repository was written in extensibility in mind. Altough this guide gets you through the process, the repository was designed for you to use it however you like it, by using the code itself.

### Setup 
I'm assuming that you have built, installed and properly configured [Tonic](https://github.com/mmajewsk/Tonic).
Also, you will need to also install this dependencie using [absolutely unholy abomination of a script](https://github.com/mmajewsk/TonicSlamDunk) ``./install.sh` - should be ok on 16.04 and 18.04.
Or use a docker (also described in that repo) [mwmajewsk/tonic_slam_dunk](https://hub.docker.com/repository/docker/mwmajewsk/tonic_slam_dunk).

Then before you start messing around with this repo, you should drive your Tonic car around, and record the video data.

```
python run.py -v -s --dump_video ~/path/to/video/dump
```

After that, you can go to the Tonic/autonomous directory. Activate the conda environment that contains SlamDunk installation (or use docker).

### 1. Run a script that creates required rgb.txt file in the data dump
```
(SlamDunkEnv2) python scripts/make_rgbtxt.py ~/path/to/video/dump
```

### 2. Create a map using map\_creator.py

First try out the dataset:

```
(SlamDunkEnv2) python map_creator.py /path_to/vocabulary_file/slam_dunk/builds/data/ORBvoc.txt /path_to/camera_calibration/os2py_applied/TUM-MINE-wide.yaml /path/to/video/dump
```

There are some options that you can use, you can change beginning and end of the images used for the map.
You can use them in reverse, or even save and load the map.
You can read data from one set of pictures, save the map, then read it with other set of pictures, improving your map. The possibilities are limitless :D 
Use options of the script to your advantage. When you are satisfied with the setup, dump the map using `--save_map`.

### 3. Use generated map to set up checkpoints

Checkpoints are points on the map that you want your car to go through.
The easiest way to use them is to first filter the images to look for those that can be used as checkpoints.

```
(SlamDunkEnv2) python filter_checkpoints.py  ~/path/to/map_dump/assoc.json ~/path/to/video/dump ~/path/to/filtered/checkpoints_filtered
```

Now choose images of the places that you want your car to get to.
From this point you have two options.

Either you write the names of the images in a text file (the car will be navigated through them in the order they) like this:

```
frame00110_1604587599.312472.jpg
frame00145_1604587601.440924.jpg
frame00211_1604587605.4512722.jpg
```

Or you create additional folder `chosen_checkpoints/` and put selected images there.

### 4. Run main.py

As this is work still in progress, for now you have edit the code of `main.py` in order to point all of the necessary paths into the right places. 
You will have to run two processes simultaenously on the car itself (i recommend using tmux).

```
python video_streaming.py
```

```
python3 steering_motors.py
```

Then simply run `(SlamDunkEnv2) python main.py`


## Further reading

graph theory books
http://www.maths.lse.ac.uk/Personal/jozef/LTCC/Graph_Theory_Bondy_Murty.pdf
http://www.esi2.us.es/~mbilbao/pdffiles/DiestelGT.pdf

hypergraph
https://www.researchgate.net/publication/339228370_Hypergraphs_an_introduction_and_review

slam tutorial
http://www2.informatik.uni-freiburg.de/~stachnis/pdf/grisetti10titsmag.pdf
