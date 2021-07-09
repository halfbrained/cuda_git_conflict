Plugin for CudaText.
Adds a convenient command to solve Git merge conflicts: 
'Plugins > Git Conflict Solver > Solve nearest conflict'.
See the intro video for VSCode:
https://www.youtube.com/watch?v=QmKdodJU-js

It finds Git conflict marker in the current document:
<<<<<<< some_name
=======
>>>>>>> some_name

It finds the nearest marker from the current vertical-scroll position,
with "wrapped search" on. And suggests actions for this conflict:
- 'Current change' - Take the upper part
- 'Incoming change' - Take the lower part
- 'Both' - Concatenate and take both parts

Author: halfbrained (https://github.com/halfbrained)
License: MIT
