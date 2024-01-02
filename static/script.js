let arr = [];
const submit = document.getElementById('submitButton')

function onClick(){
  fetch('http://localhost:5000/add')
    .then((response) => {
      return response.json();
    })
    .then((arr) => {
      const playlists = document.getElementById('playlistNames')

      while (playlists.firstChild) {
        playlists.removeChild(playlists.firstChild)
      }

      for (item of arr){
        let h1 = document.createElement('h1');
        h1.textContent = item;
        playlists.insertAdjacentElement('afterbegin', h1)
      }
      
      let songField = document.getElementById('inputSong')
      let artistField = document.getElementById('inputArtist')
      songField.value = '';
      artistField.value = '';
    }
    );
  }
  
submit.addEventListener('click', onClick)
