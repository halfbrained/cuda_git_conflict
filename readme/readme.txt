Plugin for CudaText.
Adds a convenient command to solve Git merge conflicts: 
'Plugins > Git Conflict Solver > Solve nearest conflict'.
See the intro video for VSCode:
https://www.youtube.com/watch?v=QmKdodJU-js

It finds in the current document Git conflict markers:
<<<<<<< HEAD
=======
>>>>>>> some_name

It finds the nearest markers from the caret position, with
"wrapped search" on. And suggests actions for this conflict:
- 'Current change' - Take the upper part
- 'Incoming change' - Take the lower part
- 'Both'


Author: halfbrained (https://github.com/halfbrained)

License: MIT
