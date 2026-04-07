English | [繁體中文](README.md)

# MissAV Downloader v1.0.0

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-red)

**MissAV Downloader** is an academic research tool developed for studying multimedia streaming, HLS (HTTP Live Streaming) technology, and automated crawler analysis. This project aims to explore how modern video platforms hide m3u8 resources through dynamic encrypted JavaScript and how to stably download stream segments under high-concurrency environments.

---

## ✨ Core Research Features

This project is continuously updated. The current v1.0.0 version includes the following powerful features:

* **🖥️ Modern Graphical Interface**: Built with `CustomTkinter`, supporting Light/Dark modes (system-adaptive) with an intuitive and smooth user experience.
* **🕷️ Intelligent Crawler & Filtering**:
    * Enter actress or series URLs to automatically crawl all video links across multiple pages.
    * **Smart Priority**: Automatically filters duplicate videos and allows for priority adjustment based on different versions (e.g., Uncensored Leak, Subtitled).
* **⚡ High-Speed Concurrent Download (Sponsor Only)**:
    * Utilizes multi-threading technology (`ThreadPoolExecutor`) to download `.ts` segments in parallel, maximizing bandwidth utilization.
    * **Dual Progress Bars**: Simultaneously displays "Total Task Progress" and "Single File Download Progress" for clear status monitoring.
* **⏯️ Task Control**:
    * **Pause/Resume**: Pause at any time during the download process to release network resources and resume later.
* **🔄 Consumable Task List**:
    * The download list uses "consumable" management. Once a task is completed, the URL is removed from the list.
    * If the program is interrupted or manually stopped, unfinished URLs are automatically written back to the list file, allowing for seamless resumption without duplicate downloads.
* **🛠️ Automated Processing**:
    * **Auto-Conversion**: Automatically calls FFmpeg after downloading to merge segments losslessly and convert them to `.mp4` format.
    * **Auto-Cleanup**: Features a triple cleanup mechanism (pre-task, post-conversion, and upon program exit) to ensure temporary files do not occupy disk space.

---

## 📋 Requirements

Before running this program, please ensure your computer is prepared with the following:

1.  **Python 3.8 or higher**
2.  **FFmpeg** (Essential component):
    * The program requires FFmpeg for video merging and conversion.
    * Download it from the [FFmpeg Official Website](https://ffmpeg.org/download.html).
    * **Note**: Ensure that the path to `ffmpeg.exe` is added to your system environment variable **PATH**.

---

## 🚀 Usage Guide

### Step 1: Link Crawling
* Paste the MissAV actress or series URL into the "**Target URL**" field.
* Click "**Crawl all videos from this actress/series page**".
* The program will automatically generate a URL list file and set a default storage path.

### Step 2: Batch Downloading
* Confirm that the "**URL List File**" and "**Output Folder**" paths are correct.
* Click "**Start Batch Download**".
* Monitor the download progress and Estimated Time of Arrival (ETA) via the dual progress bars at the bottom of the interface.

---

## 🔒 Security Verification & Disclaimer

### File Verification
To ensure the executable has not been tampered with, please verify the **SHA-256 Checksum** provided on the Release page after downloading the compiled version.

### Disclaimer
* **Academic Use**: This project is for personal technical learning and HLS protocol research purposes only.
* **Copyright Respect**: The copyright of the downloaded content belongs to the original creators or publishers.
* **Do not use this tool for commercial profit or any infringing activities**.
* **Legal Responsibility**: Any legal consequences arising from the use of this tool shall be borne by the user. The author assumes no legal liability.

---

## 📄 License
This project is licensed under the **MIT License**.
Copyright (c) 2026 **Pyrol**.

---

## 📩 Contact & Support
* **Technical Exchange / Sponsorship**: [pyrolloryp@proton.me](mailto:pyrolloryp@proton.me)
* **Issue Reporting**: Please submit reports via GitHub Issues.