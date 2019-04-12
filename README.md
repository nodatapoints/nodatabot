# nodatabot
This is the repository for a Telegram Bot which does miscellaneous stuff.  
End of the Story.
  
Well not really. His Name is herbert (Yes, lowercase! I also don't know why a proper name is written in lowercase,
but I guess you'll have to ask the original creator @nodatapoints about this, because I still got no answer after asking
him a third time, so I'm not positive i'll ever get to know why.)

And he was created because we, @nodatapoints, @AlcedoAttis and @CVTTSD2SI, all frequent botusers,
were itching for something more personal, more customizable and herbert is our take on that.

The current main feature is a recursive, 27x27 sized Version of TickTackToe, where you play on multiple boards to increase the
difficulty and depth while stil remaining relatively simple to understand. It's also intuitively coded
with a GUI and boxes to show where you can place something.
The game is playable by 1 to n players on a 3^mx3^m board (the implementation isn't though, having a playercount of 3 hardcoded
because it fit our needs the best.), ending when someone wins the game with the lowest depth.

herbert also features
- pinging
- html/png/gif/... files of Website contents
- WolframAlpha answers
- hashing
- calculations
- fractal carpets
- LaTeX

Arguably the best currently implemented feature and an absolute insider tip for everyone using this bot is the amazing
household math capability of herbert, impressing everyone from the layman to the current President (even if thats not that hard
https://cbsnewyork.files.wordpress.com/2015/07/gettyimages-494048423_master.jpg?w=1024&h=576&crop=1) 

> I'm very impressed <br/> -Dalei Lama

It enables you to delegate calculations like the sum of your bills to herbert, who will solve them with groundbraking speed
and without erorrs **all of the time** as long as you use floats. And that is not even half of it.
The cherry on the cake is that you can do it with multipication, too.  
Whoah man, let that sink in and realise that this is all you need in your life.
And that we generously gave you the opportunity to experience this overwhelming bliss.

<br/> <br/> <br/>
This file will get updated within "a reasonable time" (https://definitions.uslegal.com/r/reasonable-time/)
with the publication and documentation of new and existing feaures. The user currently hosting this repository is liable
for this task and can be held accountable for nondisclosure and late updates.

All work is protected under Copyright and -left; meaning that you can copy it from all sides
(at least the horizontal ones, copyup is currently dicussed in our legal division under David Rauh
(who will probably start working at 11pm for 1 hour and will still be leagues better than me tomorrow morning in the legal,
economics and law discussion D: ))

- edited and written by @AlcedoAttis


### DEPENDENCIES
#### Basic
- python-telegram-bot

#### For each Bert
- certifi
- cffi
- cryptography
- lxml
- pillow
- requests
- scrapy
- urllib3
