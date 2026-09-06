English | [繁體中文](README.md)

# MissAV Downloader v2.0.0

![Go](https://img.shields.io/badge/Go-1.25-00ADD8)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-2.0.0-orange)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Bundled-brightgreen)

**MissAV Downloader** is an academic research tool built to study multimedia streaming, HLS (HTTP Live Streaming), and automated crawling. It explores how modern video platforms hide m3u8 resources behind dynamically obfuscated JavaScript, and how stream segments can be downloaded reliably under high concurrency.

> **What's new in v2.0.0: the core has been rewritten from Python to Go.** Startup time, memory footprint, and download scheduling all improved noticeably — and **no Python installation or dependencies are required any more**. Download, extract, run.

### [⬇️ Download the latest release](../../releases/latest)

Portable Windows build — extract and run. Verify it against the [SHA-256 checksum](#file-verification) after downloading.

---

## ✨ Core Research Features

* **🖥️ Native desktop UI** — built with Go + [Wails](https://wails.io/), rendered through the system's built-in WebView2. Light/dark themes, optionally following the system setting.
* **🕷️ Smart crawling and filtering**
    * Paste an actress or series URL and every paginated video is collected into a URL list file.
    * **Smart prioritisation** — duplicates are filtered out, and you can set the preferred variant (original / Chinese subtitles / uncensored leak), with VR opt-in.
* **🛡️ Stream probing** — a separate networking component mimics browser TLS/HTTP2 fingerprints, for studying resource discovery under modern anti-bot measures.
* **⏯️ Task control**
    * **Pause / resume / stop** — free up bandwidth mid-download and pick up later.
    * **Segment-level resume** — already downloaded `.ts` segments are kept, so an interruption doesn't mean starting over.
    * **Two-level progress** — overall task progress and per-file progress side by side, with an ETA.
* **🔄 Consumable task list** — each finished task is removed from the list file; if the run is interrupted or stopped, unfinished URLs are written back so the next run resumes without re-downloading.
* **🛠️ Automation**
    * **Automatic remux** — FFmpeg (bundled, portable) losslessly merges the segments into `.mp4` when a download completes.
    * **Automatic cleanup** — temporary files are cleared before a task, after remuxing, and on exit.

---

## 🔑 Sponsor Edition Features

The Sponsor Edition is, as the name says, for **sponsors**. The features below are **visible but inactive** in the Community Edition; clicking them reports that they belong to the Sponsor Edition. Their code is not present in the Community Edition's executable, so it isn't carrying dead weight it can't use.

| Feature | Description |
| --- | --- |
| **Account sign-in** | Sign in to a missav.ai account (including shared sign-in via a browser cookie) to reach saved data on the site. |
| **Favorites** | Sync the saved actress list from the site, work out which videos haven't been downloaded yet, and browse each actress's full video list. |
| **New-release monitoring** | Check saved actresses for new videos in the background on a configurable interval, with a full deep-scan pass to catch anything missed. |
| **Local video database** | Build a local video index per saved actress, used as the baseline for new-release comparison. |
| **Tray icon and notifications** | Tray badge, Windows toast notifications, download-complete notifications, and minimise-to-tray on window close. |
| **Automatic filing** | Finished downloads are sorted into per-actress folders (solo work under the actress's name, two or more under "multiple actresses", none detected under "unclassified"). The Community Edition puts everything flat in the output folder. |
| **⚡ High-speed concurrent download** | The Community Edition pins both "concurrent downloads" and "concurrent site connections" to 1. |

### How to get the Sponsor Edition

The Community Edition is **free**, and it keeps getting updated alongside the Sponsor Edition — none of the locked features get in the way of downloading videos normally.

The Sponsor Edition is available through **sponsorship**. Keeping this project working (especially the anti-bot countermeasures after each site change) takes ongoing time, and sponsorship is what makes that sustainable.

**Email** [pyrolloryp@proton.me](mailto:pyrolloryp@proton.me) saying you'd like the Sponsor Edition, and you'll get a reply with sponsorship details and how to receive it. Technical discussion, feature suggestions and bug reports are equally welcome by email or via Issues.

The same explanation and contact address also appear at the top of the app's Settings tab.

---

## 📋 Requirements

* **Windows 10 / 11**
* **WebView2 Runtime** — already included in Windows 11 and in Windows 10 updates from 2020 onward, so you usually don't need to install anything. If the window comes up blank, install *Microsoft Edge WebView2 Runtime* from Microsoft.
* **FFmpeg** — a portable build is bundled. You do **not** need to download it or add it to PATH.

No Python, and no packages to install.

---

## 📦 Distribution Format

Releases ship as a **folder**, not a single exe. Everything is already unpacked at build time, so the program doesn't have to extract itself into a temp directory on every launch — which is what causes the system-wide multi-core CPU spike and stutter you get from single-file bundles.

* **Keep and move the whole folder**, not just the `.exe` — on its own it can't find its dependencies and won't start.
* Some antivirus software (including Microsoft Defender) real-time scans new executables and large file sets, which can add a brief stall on first launch. If you trust the source, add the program folder to your antivirus exclusion list (Windows Security → Virus & threat protection → Manage settings → Exclusions).

---

## 🚀 Getting Started

### Step 1: Collect the video list
* Paste a MissAV **single video** or **actress / series page** URL into the **Target URL** field (the "Paste" button works too).
* For an actress or series page, the program pages through the site automatically and writes every video into the URL list file.
* You can also drag a prepared `.txt` list onto the window to import it.

### Step 2: Check the download settings
* Confirm the **URL list file** and **output folder** paths.
* Tick the variants you want (original / Chinese subtitles / uncensored leak / VR).

### Step 3: Start the batch download
* Click **Start batch download** and watch progress and ETA on the two progress bars.
* You can pause or stop at any time; unfinished entries stay in the list file for the next run.

---

## 🔒 Verification and Disclaimer

### File verification
To make sure the executable hasn't been tampered with, always compare it against the **SHA-256 checksum** published on the [Release page](../../releases/latest).

### Legal notice
* **Academic use** — this project is for personal technical study and HLS protocol research only.
* **Respect copyright** — downloaded content remains the property of its original creators or distributors.
* **Do not use this tool for commercial gain or any infringing purpose.**
* **Liability** — any legal consequences arising from use of this tool rest with the user; the author accepts no liability.

---

## 📄 License
Released under the **MIT License**.
Copyright (c) 2026 **Pyrol**.

---

## ⭐ Support This Project

If this project helped your technical study or research, a **Star ⭐** (top right of the page) is much appreciated. Every star keeps the project maintained and helps other people find it.

---

## 📩 Contact and Support
* **Technical discussion / sponsorship**: [pyrolloryp@proton.me](mailto:pyrolloryp@proton.me)
* **Bug reports**: please open a GitHub Issue.
