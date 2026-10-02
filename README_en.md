English | [繁體中文](README.md)

# MissAV Downloader Go

![Go](https://img.shields.io/badge/Go-1.25-00ADD8)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/github/v/release/pyrolloryp/MissAV-Downloader-Go?label=Version&color=orange)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Bundled-brightgreen)

**MissAV Downloader Go** is an academic research tool built to study multimedia streaming, HLS (HTTP Live Streaming), and automated crawling. It explores how modern video platforms hide m3u8 resources behind dynamically obfuscated JavaScript, and how stream segments can be downloaded reliably under high concurrency.

> **What's new in v2.5.0: a task manager, a Popular tab, playlist downloads and an English interface — plus seamless merging with no gaps between segments, and automatic retries when the connection drops.** Coming from v2.0.0? See [Upgrading from v2.0.0](#upgrading-from-v200).

### [⬇️ Download the latest release](../../releases/latest)

Portable Windows build — extract and run. Verify it against the [SHA-256 checksum](#file-verification) after downloading.

---

## ✨ Core Research Features

* **🖥️ Native desktop UI** — built with Go + [Wails](https://wails.io/), rendered through the system's built-in WebView2. Light/dark themes, optionally following the system setting. The interface is available in **English and Traditional Chinese**; it follows the system language by default and can be switched in Settings at any time, no restart needed.
* **🕷️ Smart crawling and filtering**
    * Paste an actress, series or **playlist** URL and every paginated video is collected into a URL list file. Playlists download in their original order, and the list file is named after the playlist.
    * **Work category** — when crawling an actress page, choose all, solo or multi-actress works.
    * **Variant selection** — tick the variants to download (original / Chinese subtitles / uncensored leak), with VR opt-in. The Community Edition downloads **every variant you tick**: if a code exists as both the original and a Chinese-subtitle release, both are downloaded, with `[中文字幕]` / `[無碼流出]` appended to the filename so they never overwrite each other. If you only want the original, tick only "Original".
    * Duplicate URLs for the same video are removed automatically.
* **🔥 Popular** — browse today's, this week's and this month's rankings, enlarge covers, and add the videos you tick straight to the download list. Which ranking opens first can be set in Settings.
* **🛡️ Stream probing** — a separate networking component mimics browser TLS/HTTP2 fingerprints, for studying resource discovery under modern anti-bot measures.
* **📋 Task manager**
    * An imported TXT becomes a **batch**, and each video's progress is stored locally, so it's still there after you close and reopen the app (nothing starts downloading on its own).
    * Failed or stopped videos can be retried individually; unfinished URLs can be exported, and completed records cleared.
    * TXT lists in the download folder are picked up automatically at startup; re-crawling the same list merges it back into its existing batch, so videos already downloaded aren't fetched again.
    * **Pause / resume / stop**, **segment-level resume** (downloaded `.ts` segments are kept, so an interruption doesn't mean starting over), **two-level progress** with an ETA, and the list scrolls itself to the video currently downloading.
* **🛠️ Automation**
    * **Seamless merging** — FFmpeg (bundled, portable) losslessly merges the segments into `.mp4` when a download completes. Segments are streamed to FFmpeg in order, so there are no gaps at the joins and the duration matches the source stream.
    * **Automatic retries** — brief connection drops are retried automatically, failed segments are fetched again at the end, and a video only fails after two straight minutes without receiving any data.
    * **Full filenames** — files are named with the full title shown on the video page, shortened automatically when too long. The final filename is only written once merging succeeds, so stopping midway never leaves a broken file behind.
    * **Download while merging** — the next video starts downloading while the previous one is still being merged.
    * **Temp cleanup** — each video's temporary segments are deleted as soon as it finishes merging; unfinished segments are kept for resuming and can be cleared from Settings with one click.

---

## 🔑 Sponsor Edition Features

Everything listed above works fully in the Community Edition. The Sponsor Edition is, as the name suggests, for **sponsors**; it adds everything listed below.

None of that code ships inside the Community Edition's executable — these features aren't switched off, they simply aren't built in. So the Community Edition isn't carrying dead weight it can't use, and it does nothing in the background while it sits idle: no scheduled connections, no CPU usage.

| Feature | Description |
| --- | --- |
| **Account sign-in** | Sign in to a missav.ai account (including shared sign-in via a browser cookie) to access the actresses you've saved on the site. |
| **Collections** | Sync the saved actress list from the site, work out which videos haven't been downloaded yet, and browse each actress's full video list. The saved videos and playlists from your site account are listed too, ready to check and add to the download list. The Community Edition's Collections tab opens, but the list is always empty. |
| **New-release monitoring** | Check saved actresses for new videos in the background on a configurable interval, with a full deep-scan pass to catch anything missed; videos newly added to tracked playlists are reported too. The Community Edition has **no background checker at all** — when it's idle it is genuinely idle, and it will never pop up a "new release found" notification on its own. |
| **Local video database** | Build a local video index per saved actress, used as the baseline for new-release comparison. **Crawling itself is fully available in the Community Edition** — it still pages through the site and still writes the URL list. Only the step that files a crawled list into the database is sponsor-only. |
| **Tray icon and notifications** | Tray icon with an unread badge, Windows toast notifications, download-complete notifications, and minimize-to-tray on window close. The Community Edition has none of this: no icon in the notification area, no system notifications of any kind, and closing the window really does quit. Track downloads from the task progress in the app instead. |
| **Automatic filing** | Finished downloads are sorted into per-actress folders (solo work under the actress's name, two or more under "multiple actresses", none detected under "unclassified"), and a playlist download goes into a folder named after the playlist. The Community Edition puts everything flat in the output folder — no "multiple actresses" or "unclassified" folders are ever created. **The videos themselves, their filenames and their quality are identical**; you just end up with one flat pile that you have to organize yourself. |
| **List import rules** | When a code exists in several variants, download only one of them, in a version priority you choose (for example uncensored leak first, then Chinese subtitles). The Community Edition always downloads **every variant you tick** — tick fewer to download fewer. |
| **Clip preview** | Preview a short clip right inside the Popular and Collections lists (starting from any minute you choose), and open the original page in one click. These two buttons don't appear in the Community Edition's lists; enlarging covers works in both editions. |
| **⚡ Multiple downloads at once** | The Sponsor Edition downloads up to 5 videos concurrently (3 by default); the Community Edition works through the queue **one video at a time**. **A single video downloads at exactly the same speed in both editions** — what's limited is how many run at once, not how fast each one goes. |
| **🎞️ Video quality selection** | Choose the download quality up front: highest (default), up to 1080p, up to 720p, up to 480p, or lowest — useful when disk space or bandwidth is tight. **The Community Edition always downloads at the highest quality**: for the same video, both editions pull the same stream, the same bitrate and the same file size. Nothing is downgraded — what the Sponsor Edition adds is the ability to deliberately dial it *down*. |

### What the Community Edition's UI looks like

These features are **deliberately left visible** in the Community Edition, so you can see what they are and what sponsorship would add. In practice:

* **Buttons** (sign in, refresh favorites, build database, test notification…) show a short note when clicked, telling you it's a Sponsor Edition feature and how to get in touch — no error, no dead click.
* **Toggles** (monitoring, the various notifications, "start downloading immediately after adding"…) can be switched on, but **they revert to off when settings are saved**. That's intentional: a switch stuck in the "on but doing nothing" state looks like a bug, so it honestly falls back to off.
* **Dropdowns** (concurrent site connections, concurrent downloads, video quality, close-window behavior) only list the option that applies to the Community Edition: the first two are fixed at 1, quality is fixed at the highest, and closing the window quits.
* **List import rules** are fixed to "download all selected types", and the version priority can't be changed.
* **Check interval** can be changed and will be saved, but it only feeds favorites monitoring and database building — ordinary downloading and crawling don't go through it.

The Community Edition also **ships with the right defaults already set**: monitoring and notifications start off, concurrent downloads starts at 1. There's nothing you need to turn off yourself.

### How to get the Sponsor Edition

The Community Edition is **free**, and it keeps getting updated alongside the Sponsor Edition — same source, same version number, same download engine. None of the locked features get in the way of downloading videos normally.

The Sponsor Edition is available through **sponsorship**. Keeping this project working (especially the anti-bot countermeasures after each site change) takes ongoing time, and sponsorship is what makes that sustainable.

**Email** [pyrolloryp@proton.me](mailto:pyrolloryp@proton.me) saying you'd like the Sponsor Edition, and you'll get a reply with sponsorship details and how to receive it. Technical discussion, feature suggestions and bug reports are equally welcome by email or via Issues.

The same explanation and contact address also appear at the top of the app's Settings tab.

---

## 📋 Requirements

* **Windows 10 / 11**
* **WebView2 Runtime** — already included in Windows 11 and in Windows 10 updates from 2020 onward, so you usually don't need to install anything. If the window comes up blank, install the [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) from Microsoft.
* **FFmpeg** — a portable build is bundled. You do **not** need to download it or add it to PATH.

No Python, and no packages to install.

---

## 📦 Distribution Format

The Community Edition is currently **released for Windows only**.

Releases ship as a **folder**, not a single exe. Everything is already unpacked at build time, so the program doesn't have to extract itself into a temp directory on every launch — which is what causes the system-wide multi-core CPU spike and stutter you get from single-file bundles.

* **Keep and move the whole folder**, not just the `.exe` — on its own it can't find its dependencies and won't start.
* Some antivirus software (Microsoft Defender included) scans new executables and large sets of files in real time, which can cause a brief stall on first launch. If you trust the source, add the program folder to your antivirus exclusion list (Windows Security → Virus & threat protection → Manage settings → Exclusions).

### Upgrading from v2.0.0

From v2.5.0 the executable is named `MissAVDownloaderGo.exe` (it used to be `MissAV_Downloader.exe`).

1. Extract the new version into a **new folder**.
2. Move `data` (settings) and `downloads` (URL list files and videos) over from the old folder. If you have half-finished downloads, move `temp` as well and they'll resume.
3. Open the new version, check that your settings and lists are there, then delete the old folder.

Videos you downloaded with the old version won't be downloaded again: the new version names files with the full title, but recognizes both the old and the new filenames when checking what's already downloaded. TXT lists in `downloads` are imported into the task manager at startup; nothing starts downloading on its own.

---

## 🚀 Getting Started

### Step 1: Collect the video list
* Paste a MissAV **single video**, **actress / series page** or **playlist** URL into the **Target URL** field (the "Paste" button works too).
* For an actress, series or playlist page, the program pages through the site automatically, writes every video into the URL list file, and creates a batch in the task manager.
* You can also drag a prepared `.txt` list onto the window to import it, or tick videos in the **Popular** tab and click **Add to download list**.

### Step 2: Check the download settings
* Confirm the **URL list file** and **Save folder** paths.
* Tick the variants you want (original / Chinese subtitles / uncensored leak / VR); when crawling an actress page you can also pick a **work category** (all / solo / multi-actress).

### Step 3: Start the batch download
* Pick the batch in the **Task manager**, click **Start batch download**, and watch progress and ETA on the two progress bars.
* You can pause or stop at any time; unfinished videos stay in the batch, so selecting the same batch next time resumes them, and failed videos can be retried individually.

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
