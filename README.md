# cybot


Attempting to make a generic socket.io bot. Currently framed for cytu.be. Running on Python36 and SocketIo v1.x (but will be upgrading to v2).


* Allows generic message routing for alternative bot's, or specific user's commands.
* Has some simple functions built for solving anagrams, voteskipping the current media.
  * Will be working on converting some functions to accept the new Msg object.
* The Msg class is as simple as possible; Msg attempts to add a generic way to handle messages
