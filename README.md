<p align="center">
    <h1 align="center">KOMETA_FILES</h1>
</p>
<p align="center">
    <em><code>❯ REPLACE-ME</code></em>
</p>
<p align="center">
	<!-- Shields.io badges disabled, using skill icons. --></p>
<p align="center">
		<em>Built with the tools and technologies:</em>
</p>
<p align="center">
	<a href="https://kometa.wiki/en/latest/">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/png/kometa.png" width="75" height="75"> 
	<a href="https://www.themoviedb.org">
		<img src="https://cdn6.aptoide.com/imgs/2/f/0/2f00b070ae69de52adb50055ec150ef9_icon.png?w=128" width="75" height="75">
	<a href="https://www.thetvdb.com">
		<img src="https://cdn.jsdelivr.net/gh/selfhst/icons/png/tvdb.png" width="75" height="75"> 
	<a href="https://fanart.tv">
		<img src="https://avatars.githubusercontent.com/u/18613905?s=200&v=4" width="75" height="75"> 
	</a></p>

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

<code>❯ Kometa_Files is my repository for premade, properly mapped, Kometa Files. The individual files make it possible to pick and choose the ones you'd like, or use them all. </code>

---

## 👾 Features

<code>❯ Prebuilt Kometa files that pull everything together for a well groomed media server. Pulling the respective files will create a collection add custom posters. With collections like MonsterVerse or Lord of The Rings / Middle Earth there is a corisponding TV Shows collection as well and can all be viewed on one ease collection. </code>

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
