# Placement

#### Video Demo:  https://youtu.be/rqahvBhgIoQ

## User Description:

 Placement is my final project for Harvard's CS50X; thus I used the opportunity to solve a problem that has plagued me for years. That is, not knowing which of my playlists a specific song should go into. Placement solves that exact problem.

 All you have to do is sign in with your Spotify account and submit the song name and artist. Placement will then make a genre profile of each playlist you have, and find where the song you queried would best fit. The playlist or playlists will then be displayed on the screen directly below the form.

## Technical Description:

The actual logic of Placement behaves in a very intuitive way. The Spotify API will give access a lot of information on specific songs, playlists, or the current user. With that we can begin to find out which one of the users playlists the requested song should go into.

First we start by making a API request for all the current user's playlist. From there we go into each playlist and select 50 songs with a random offset for each playlist. Then we find each song's artist, and then we can get the genre of each artist. With that information we can then populate a profile of genres for each playlist, then giving us a good idea of what kind of songs comprise it.

Now that we have the user playlists profiles out of the way, we can focus on the requested song. The process is much the same for the playlists. We make an API request searching for the imputed song using the song name and artist from the form. Then we use the response to find the artist genres, and assign them to a variable

Lastly we then compare the input song genres with the playlists genre profiles and return the playlist or playlists with the most similarities. Once that is done we display the top three playlists to the user by means of Javascript inserting elements to the webpage.


## Challenges:

This project was by far the most challenging application I've ever tried to develop. Every step along the way required a multitude of patience, time, and research. From utilizing the Spotify API, implementing OAUTH, creating logic for functions, and optimizing the runtime using threading, this project had many learning curves.

One of the biggest hurdles was the runtime of the application. Before I started work on making it faster, it would take up to fifteen seconds per song entry. I realized very quickly that API calls are very time inefficient, but even after minimizing API calls as much as I could It only helped moderately. 

After I spent some time thinking about what I could do to speed up the process I had a realization. I was going through the user's playlists and making genre profiles for them for every single user submission. Not only that, but I was also waiting till the user pressed submit before starting that process when that information was already accessible to me. So with that said, by going through the user's playlist as soon as the page loaded using threading and assigning the results to a global variable, I was able to cut down the runtime significantly and provide a usable solution

All and all, this project was a great learning process. It taught me about creating and utilizing APIs, routing, debugging, UI/UX, and optimizing a program that already functions. All while working to solve a problem I am passionate about. I was a rewarding project and I'm very proud of the end result.