<p align="center">
    <h1 align="center">KOMETA_FILES</h1>
</p>

<p align="center">
	<!-- Shields.io badges disabled, using skill icons. --></p>
<p align="center">
		<em>Built with these tools and technologies:</em>
</p>
<p align="center">
	<a href="https://kometa.wiki/en/latest/" title="Kometa">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/png/kometa.png" width="60" height="60"></a>

<br>
	<a href="https://mediux.pro/" title="MediUX">
	<img src="https://mediux.pro/mediux.svg" width="40" height="40"></a>
 
  <a href="https://www.themoviedb.org/" title="TMDB">
	<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/tmdb.svg" width="40" height="40"></a>
  <a href="https://code.visualstudio.com" title="Visual Studio Code"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Visual_Studio_Code_1.35_icon.svg/2048px-Visual_Studio_Code_1.35_icon.svg.png" width="40" height="40"></a>
   <a href="https://gimp.org" title="GIMP"><img src="https://upload.wikimedia.org/wikipedia/commons/5/55/GIMP_Icon.png" width="40" height="40"></a>



<br>
  <a href="https://radarr.video" title="Radarr">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/radarr.svg" width="30" height="30"></a>
	<a href="https://sonarr.tv" title="Sonarr">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/sonarr.svg" width="30" height="30"></a>
  <a href="https://www.thetvdb.com" title="TVDB">
	<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/tvdb.svg" width="30" height="30"></a>
 	<a href="https://picsart.com/" title="Picsart"><img src="https://github.com/Wikid82/kometa_files/blob/main/images/.readme/picsart.png?raw=true" width="30" height="30"></a>
 	<a href="https://trakt.tv/" title="Trakt"><img src="https://trakt.tv/assets/logos/logomark.square.gradient-b644b16c38ff775861b4b1f58c1230f6a097a2466ab33ae00445a505c33fcb91.svg" width="30" height="30"></a>
  <a href="https://theposterdb.com" title="ThePosterDB">
	<img src="https://theposterdb.com/assets/logos/icon/color.svg" width="30" height="30"></a>
  <a href="https://fanart.tv/" title="FanArt.tv">
	<img src="https://github.com/Wikid82/kometa_files/blob/main/images/.readme/fanart.png?raw=true" width="30" height="30"></a>


<br>

Table of Contents

- [📍 Overview](#-overview)
- [👾 Features](#-features)
- [📂 Repository Structure](#-repository-structure)
- [🚀 Getting Started](#-getting-started)
    - [🔖 Prerequisites](#-prerequisites)
    - [📦 Installation](#-installation)
- [🤝 Contributing](#-contributing)
- [🙌 Acknowledgments](#-acknowledgments)

<hr>

## 📍 Overview

<code>❯ My files' artwork are based on the positioning of the overlays I use. You may prefer different overlays in different positions. Feel free to use these files as a template. Just replace the image urls with your prefered links. See you in the rabbit hole!  </code>

<code>❯ ?foo=bar: What does that mean?
  I can't always find premade posters that I like. When I don't, I make my own. Once they are in Plex, sometimes I don't like them as much as I thought and I do little tweeks. MediUX does not generate a new link when updating a file. I apply the ?foo=bar (thanks to a mod in the Kometa Reddit for the idea). This then fools the Kometa cache that its a new link and will download the updated poster.   </code>

---

## 👾 Features

<code>❯ Prebuilt Kometa files that pull everything together for a well groomed media server. Pulling the respective files will create a collection and add custom matching (as much as possible) posters. With collections like MonsterVerse or Lord of The Rings there is a corisponding TV Shows collection as well and can all be viewed in one easy collection. </code>

---

## 📂 Repository Structure

```sh
└── kometa_files/
    ├── .github
    │   └── ISSUE_TEMPLATE
    ├── images
    ├── media libraries
    │   ├── movies
    │   │     ├── collections
    │   │     ├── metadata
    │   │     └── overlays
    │   └── series
    │         ├── collections
    │         ├── metadata
    │         └── overlays    
    ├── playlists
    ├── README.md 
    └── config.yml.template
```

## 🚀 Getting Started

### 🔖 Prerequisites

**Kometa** 

### 📦 Installation

In your Kometa config file add:
```
  Movies:
    metadata_files:
    - folder: /config/movies/metadata
    collection_files:
    - folder: /config/movies/collections
    overlay_files:
    - folder: /config/movies/overlays
```
```
  TV Shows:
    metadata_files:
    - folder: /config/series/metadata
    collection_files:
    - folder: /config/series/collections
    overlay_files:
    - folder: /config/series/overlays
```
```
 playlist_files:
    - folder: /config/playlists
```

Extract the files to their respective folders. Kometa will read the folder of files so you don't have to add each file indifidually. More on that <a href="https://kometa.wiki/en/latest/config/files/#location-types-and-paths">here</a>

Files can also be used by adding a Custom Repo. More on that <a href="https://kometa.wiki/en/latest/config/settings/?h=custom_repo#attributes">here</a> and <a href="https://kometa.wiki/en/latest/config/files/#location-types-and-paths">here</a>


## 🤝 Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Report Issues](https://github.com/Wikid82/kometa_files/issues)**: Submit bugs found or log feature requests for the `kometa_files` project.
- **[Join the Discussions](https://github.com/Wikid82/kometa_files/discussions)**: Share your insights, provide feedback, or ask questions.

<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/Wikid82/kometa_files/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=Wikid82/kometa_files">
   </a>
</p>
</details>

---

## 🙌 Acknowledgments

- Readme built with <a href="https://readme-ai.streamlit.app">ReadMe.AI</a> 

---
<p align="center"><a href="https://www.buymeacoffee.com/Wikid82" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a></p>

<p style="font-size: 50%;" align="center"> Support is not necessary, but greatly appriciated. It goes to expanding the server to test requests. If you fave a request,  <a href="https://github.com/Wikid82/kometa_files/issues"> submit it here. </p></a>