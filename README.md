# UniversalViewMatrixFinder
This is my own take on a ViewMatrix finder that works universally written in Python 3.11
# How it works
You find the general memory "region" of where the viewmatrix is stored, Because you never know where it is exactly but you know where the address "kind of is at" you put in an address near it and it will scan in 2 directions, up and down the memory by 2, 4, 6, 8, bytes (whatever the user picks) and it will take all 4x4 variables and try to use the integers of those variables to convert the 3D space to 2D space and draw a line starting from 0,0 of the screen to the player. You select where the player is on the screen (Top Left->Bottom Right) and it will start looping through. It will check each address and for each address it will check if it detects the color of the draw line inside the box of where you selected (where the player should be on screen) and if it detects the color of the line in it, it will check the end position and check if the cords align inside of the box you selected and if so it will check if the line aligns to the player body when camera moves or player moves and if so the viewmatrix is found.

This is an old source from like July of 2023 when I made it and I have not updated it since, I just found this going through my old drive and decided to post it (cause I thought I lost the project)

**Video:** https://www.youtube.com/watch?v=RGMw7Wu7qKY
![Screenshot](https://raw.githubusercontent.com/i32-Sudo/UniversalViewMatrixFinder/main/image_2024-08-07_232742350.png)
