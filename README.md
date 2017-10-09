# cybot


Another socketio bot. Currently framed for cytu.be. Running on Python36 and SocketIo v2.x.


* Allows generic message routing for alternative bot's, or specific user's commands.
* Has some simple functions built for solving anagrams, voteskipping the current media.
  * Will be working on converting some functions to accept the new Msg object.
* The Msg class is as simple as possible; Msg attempts to add a generic way to handle messages
* Has wallet and currency functionality for in-chat debit and crediting.
* Giphy, themoviedb API searches.

#### Message Prefixes
The handlemsg function allows for dynamic function calls so there's no need to define anything other than the function.

* chat_<function_name> will allow for that message to be called from the global/open chat. (ex: chat_choose)
* pm_<function_name> functions will only continue code execution if the command was PM'd. (ex: pm_debug)


#### Cost & Wallet
A wallet-like functionality to allow for points or currency. The user wallet is saved to a sqlite db. You can configure the costs of functions in the config (see cost: giphy). This will be executed _before_ the function is called.

* You can also access the wallet directly in the function if you want to manipulate currency for a particular chat function call.

#### Trailers
This, like most of the functions, is http://cytu.be specific. It takes a list of currently polling film and movies and attempts to find the trailers and then add them to the next-in-queue.

* Currently searching themoviedb (api setup in config), will expand to search Youtube.


###### TODO:
* Organize the package and fill in requirements.
* Fix trailers to work for movies with numbers in their title. (Se7en)
* Work on admin/mod "subchat" (over the wire encryption on the same socket)

