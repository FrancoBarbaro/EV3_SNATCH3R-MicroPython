# EV3_SNATCH3R_MicroPython
Infrared beacon seeking program for ev3dev2 based on the robot design and program from the 'SNATCH3R' section in "The Lego Mindstorms EV3 Discovery Book" by Laurens Valk

The purpose of the program is to make the EV3 find the infrared remote and grab it with the claw controlled by the medium motor, turn around, release it, and back away. The beacon which is activated by the top button on the infrared remote must be on for the robot to detect the remote.

The program is pretty much the same as in the book but with 3 slight modifications to make it work better:
1) If the robot set too close to the beacon at the beginning, the original program would skip the search, I changed it so that it searches at least once
2) As the arm releases the remote, the original program assumed that when it goes all the way down the value will be 0, this isn't always the case, for example the lowest it got for me was 48, so I changed it to detect a the decrease in degrees until it stops decreasing and then it will exit the release loop
3) I changed the forward movement after the robot says "detected" from the original program's 1 rotation to 0.7 because the original would go knock the remote over
