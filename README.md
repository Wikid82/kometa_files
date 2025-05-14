<p align="center"><a href="https://www.buymeacoffee.com/Wikid82" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a></p>

<p style="font-size: 50%;" align="center"> Support is not necessary, but greatly appriciated. It goes to expanding the server to test requests. If you fave a request,  <a href="https://github.com/Wikid82/kometa_files/issues"> submit it here. </p></a>

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
	<a href="https://radarr.video" title="Radarr">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/radarr.svg" width="60" height="60"></a>
	<a href="https://sonarr.tv" title="Sonarr">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/sonarr.svg" width="60" height="60"></a>
  <a href="https://trakt.tv">
 	<a href="https://www.themoviedb.org/" title="TMDB">
	<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/tmdb.svg" width="60" height="60"></a>
  <a href="https://www.thetvdb.com" title="TVDB">
	<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/tvdb.svg" width="60" height="60"></a>
 	<a href="https://trakt.tv/" title="Trakt">   
  <img src="https://trakt.tv/assets/logos/logomark.square.gradient-b644b16c38ff775861b4b1f58c1230f6a097a2466ab33ae00445a505c33fcb91.svg" width="60" height="60"></a>
	<a href="https://mediux.pro/" title="MediUX">
	<img src="https://mediux.pro/mediux.svg" width="60" height="60"></a>
  <a href="https://theposterdb.com" title="ThePosterDB">
	<img src="https://theposterdb.com/assets/logos/icon/color.svg" width="60" height="60"></a>
  <a href="https://fanart.tv/" title="FanArt">
	<img src="https://i2.wp.com/fanart.tv/images/fanart-logo.png" width="60" height="60"></a>


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

---

## 👾 Features

<code>❯ Prebuilt Kometa files that pull everything together for a well groomed media server. Pulling the respective files will create a collection and add custom matching (as much as possible) posters. With collections like MonsterVerse or Lord of The Rings there is a corisponding TV Shows collection as well and can all be viewed in one easy collection. </code>

---

## 📂 Repository Structure

```sh
└── kometa_files/
    ├── .github
    │   └── ISSUE_TEMPLATE
    ├── README.md
    ├── collections
    │   ├── movies
    │   └── tvshows
    ├── metadata
    │   ├── movies
    │   └── tvshows
    ├── overlays
    │   ├── movies
    │   └── tvshows
    └── playlists
```

## 🚀 Getting Started

### 🔖 Prerequisites

**Kometa** 

### 📦 Installation

In your Kometa config file add:
```
  Movies:
    metadata_files:
    - folder: /config/metadata/movies
    collection_files:
    - folder: /config/collections/movies
    overlay_files:
    - folder: /config/overlays/movies
```
```
  TV Shows:
    metadata_files:
    - folder: /config/metadata/tvshows
    collection_files:
    - folder: /config/collections/tvshows
    overlay_files:
    - folder: /config/overlays/tvs
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
