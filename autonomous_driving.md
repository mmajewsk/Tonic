# How to run this as autonomous car

## Setup of a map

Firstly, you need to create map of the environment.
To do this, run Tonic car with video dumping (at least), as it is specified in the main readme.

Secondly, install environment for orbslam python binding with this repo https://github.com/mmajewsk/TonicSlamDunk



Then use a script XXXXX to save orb slam map.
Then read it to obj file using script YYYYYYY, view the map and pick points that you would like to go through.
Create a list of points like this 

```
frame00375_1561984031.9048347.jpg
frame00375_1561984031.9048347.jpg
...
frame00375_1561984031.9048347.jpg
```
The run the scr ZZZZZZZZZ that will change it into set of points for the Tonic software to go through.
Then run Tonic with MMMMMMMM option.