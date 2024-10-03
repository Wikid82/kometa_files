<p align="center">
    <h1 align="center">KOMETA_FILES</h1>
</p>

<p align="center">
	<!-- Shields.io badges disabled, using skill icons. --></p>
<p align="center">
		<em>Built with the tools and technologies:</em>
</p>
<p align="center">
	[<a href="https://kometa.wiki/en/latest/">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/png/kometa.png" width="75" height="75">][1]
	<a href="https://radarr.video">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/radarr.svg" width="75" height="75">
	<a href="https://sonarr.tv">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/sonarr.svg" width="75" height="75"> 
<a href="https://trakt.tv">
  <img src="https://d3sxshmncs10te.cloudfront.net/icon/free/svg/2945267.svg?token=eyJhbGciOiJoczI1NiIsImtpZCI6ImRlZmF1bHQifQ__.eyJpc3MiOiJkM3N4c2htbmNzMTB0ZS5jbG91ZGZyb250Lm5ldCIsImV4cCI6MTcyODA3MzM1MiwicSI6bnVsbCwiaWF0IjoxNzI3ODE0MTUyfQ__.19ab2476e4821ded424bcca00cebcdf97e65f9e45dc6cc722ad8cc27e0800191"width="75" height="75">
	<a href="https://theposterdb.com" >
		<img src="https://theposterdb.com/assets/logos/icon/color.svg" width="75" height="75"> 
	</a></p>
[1]: https://kometa.wiki/en/latest/                                            "Kometa"
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

<code>❯ When I found Kometa, I also found myself coding files more than actually watching the media I have on my server. Spend less time coding them yourself. Kometa_Files is my repository for premade, properly mapped, Kometa Files. The individual files make it possible to pick and choose the ones you'd like, or use them all. </code>

---

## 👾 Features

<code>❯ Prebuilt Kometa files that pull everything together for a well groomed media server. Pulling the respective files will create a collection and add custom matching (as much as possible) posters. With collections like MonsterVerse or Lord of The Rings there is a corisponding TV Shows collection as well and can all be viewed in one easy collection. </code>

---

## 📂 Repository Structure

```sh
└── kometa_files/
    ├── .github
    │   └── ISSUE_TEMPLATE
    ├── collections
    │   ├── movies
    │   └── tvshows
    └── metadata
        ├── movies
        └── tvshows
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
```
```
  TV Shows:
    metadata_files:
    - folder: /config/metadata/tvshows
    collection_files:
    - folder: /config/collections/tvshows
```
```
 playlist_files:
    - folder: /config/playlists
```

Extract the files to their respective folders. Kometa will read the folder of files so you don't have to add each file indifidually. More on that <a href="https://kometa.wiki/en/latest/config/files/#location-types-and-paths">here</a>

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

- List any resources, contributors, inspiration, etc. here.

---
