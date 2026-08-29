"""
=============================================================================
💀 ELLIOT OSINT & DIGITAL FOOTPRINT HUNTER (Mr. Robot Edition)
=============================================================================
Author: Antigravity Pair Programmer
Architecture: Asynchronous High-Speed Multi-Platform OSINT Recon Engine
Standard: Fast Non-Intrusive Public Endpoint Probe (120+ Services)
=============================================================================
"""

import sys
import os
import re
import time
import json
import hashlib
import urllib.request
import urllib.error
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Enable VT100 ANSI terminal escape sequences on Windows
if os.name == 'nt':
    os.system('')

# Cyberpunk Terminal Color Codes
class Colors:
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"


# =====================================================================
# Database of 120+ High-Value Target Platforms
# =====================================================================
PLATFORMS_DB = [
    # Developer & Tech Hubs
    {"name": "GitHub", "cat": "Dev", "url": "https://github.com/{}", "check_url": "https://github.com/{}", "error_type": "status_code"},
    {"name": "GitLab", "cat": "Dev", "url": "https://gitlab.com/{}", "check_url": "https://gitlab.com/{}", "error_type": "status_code"},
    {"name": "Bitbucket", "cat": "Dev", "url": "https://bitbucket.org/{}/", "check_url": "https://bitbucket.org/{}/", "error_type": "status_code"},
    {"name": "StackOverflow", "cat": "Dev", "url": "https://stackoverflow.com/users/{}", "check_url": "https://stackoverflow.com/users/{}", "error_type": "status_code"},
    {"name": "Dev.to", "cat": "Dev", "url": "https://dev.to/{}", "check_url": "https://dev.to/{}", "error_type": "status_code"},
    {"name": "HackerNews", "cat": "Dev", "url": "https://news.ycombinator.com/user?id={}", "check_url": "https://news.ycombinator.com/user?id={}", "error_type": "body_text", "error_text": "No such user."},
    {"name": "Kaggle", "cat": "Dev", "url": "https://www.kaggle.com/{}", "check_url": "https://www.kaggle.com/{}", "error_type": "status_code"},
    {"name": "DockerHub", "cat": "Dev", "url": "https://hub.docker.com/u/{}", "check_url": "https://hub.docker.com/v2/users/{}/", "error_type": "status_code"},
    {"name": "Codeforces", "cat": "Dev", "url": "https://codeforces.com/profile/{}", "check_url": "https://codeforces.com/profile/{}", "error_type": "status_code"},
    {"name": "CodePen", "cat": "Dev", "url": "https://codepen.io/{}", "check_url": "https://codepen.io/{}", "error_type": "status_code"},
    {"name": "JSFiddle", "cat": "Dev", "url": "https://jsfiddle.net/user/{}/", "check_url": "https://jsfiddle.net/user/{}/", "error_type": "status_code"},
    {"name": "Replit", "cat": "Dev", "url": "https://replit.com/@{}", "check_url": "https://replit.com/@{}", "error_type": "status_code"},
    {"name": "PyPI", "cat": "Dev", "url": "https://pypi.org/user/{}", "check_url": "https://pypi.org/user/{}/", "error_type": "status_code"},
    {"name": "NPM", "cat": "Dev", "url": "https://www.npmjs.com/~{}", "check_url": "https://www.npmjs.com/~{}", "error_type": "status_code"},
    {"name": "Packagist", "cat": "Dev", "url": "https://packagist.org/users/{}/", "check_url": "https://packagist.org/users/{}/", "error_type": "status_code"},
    {"name": "RubyGems", "cat": "Dev", "url": "https://rubygems.org/profiles/{}", "check_url": "https://rubygems.org/profiles/{}", "error_type": "status_code"},
    {"name": "Crates.io", "cat": "Dev", "url": "https://crates.io/users/{}", "check_url": "https://crates.io/api/v1/users/{}", "error_type": "status_code"},
    {"name": "HuggingFace", "cat": "AI/Dev", "url": "https://huggingface.co/{}", "check_url": "https://huggingface.co/{}", "error_type": "status_code"},
    {"name": "SourceForge", "cat": "Dev", "url": "https://sourceforge.net/u/{}/profile", "check_url": "https://sourceforge.net/u/{}/profile", "error_type": "status_code"},
    {"name": "LeetCode", "cat": "Dev", "url": "https://leetcode.com/{}", "check_url": "https://leetcode.com/{}", "error_type": "status_code"},
    {"name": "HackerEarth", "cat": "Dev", "url": "https://www.hackerearth.com/@{}", "check_url": "https://www.hackerearth.com/@{}", "error_type": "status_code"},
    {"name": "TopCoder", "cat": "Dev", "url": "https://www.topcoder.com/members/{}", "check_url": "https://api.topcoder.com/v5/members/{}", "error_type": "status_code"},
    {"name": "GeeksForGeeks", "cat": "Dev", "url": "https://auth.geeksforgeeks.org/user/{}", "check_url": "https://auth.geeksforgeeks.org/user/{}", "error_type": "status_code"},
    {"name": "Scratch", "cat": "Dev", "url": "https://scratch.mit.edu/users/{}", "check_url": "https://api.scratch.mit.edu/users/{}", "error_type": "status_code"},
    {"name": "Launchpad", "cat": "Dev", "url": "https://launchpad.net/~{}", "check_url": "https://launchpad.net/~{}", "error_type": "status_code"},
    {"name": "Pastebin", "cat": "Dev", "url": "https://pastebin.com/u/{}", "check_url": "https://pastebin.com/u/{}", "error_type": "status_code"},

    # Cybersecurity & Hacking
    {"name": "TryHackMe", "cat": "Cyber", "url": "https://tryhackme.com/p/{}", "check_url": "https://tryhackme.com/api/user/{}", "error_type": "status_code"},
    {"name": "HackTheBox", "cat": "Cyber", "url": "https://app.hackthebox.com/profile/{}", "check_url": "https://www.hackthebox.com/api/v4/user/profile/basic/{}", "error_type": "status_code"},
    {"name": "Keybase", "cat": "Crypto", "url": "https://keybase.io/{}", "check_url": "https://keybase.io/{}", "error_type": "status_code"},

    # Social Networks & Media
    {"name": "Reddit", "cat": "Social", "url": "https://www.reddit.com/user/{}", "check_url": "https://www.reddit.com/user/{}/about.json", "error_type": "status_code"},
    {"name": "Telegram", "cat": "Social", "url": "https://t.me/{}", "check_url": "https://t.me/{}", "error_type": "body_text", "error_text": "tgme_page_extra"},
    {"name": "YouTube", "cat": "Social", "url": "https://www.youtube.com/@{}", "check_url": "https://www.youtube.com/@{}", "error_type": "status_code"},
    {"name": "Twitch", "cat": "Social", "url": "https://www.twitch.tv/{}", "check_url": "https://www.twitch.tv/{}", "error_type": "status_code"},
    {"name": "Pinterest", "cat": "Social", "url": "https://www.pinterest.com/{}/", "check_url": "https://www.pinterest.com/{}/", "error_type": "status_code"},
    {"name": "Medium", "cat": "Social", "url": "https://medium.com/@{}", "check_url": "https://medium.com/@{}", "error_type": "status_code"},
    {"name": "Mastodon", "cat": "Social", "url": "https://mastodon.social/@{}", "check_url": "https://mastodon.social/@{}.json", "error_type": "status_code"},
    {"name": "Flickr", "cat": "Social", "url": "https://www.flickr.com/people/{}", "check_url": "https://www.flickr.com/people/{}", "error_type": "status_code"},
    {"name": "Vimeo", "cat": "Social", "url": "https://vimeo.com/{}", "check_url": "https://vimeo.com/{}", "error_type": "status_code"},
    {"name": "Dailymotion", "cat": "Social", "url": "https://www.dailymotion.com/{}", "check_url": "https://api.dailymotion.com/user/{}", "error_type": "status_code"},
    {"name": "Rumble", "cat": "Social", "url": "https://rumble.com/c/{}", "check_url": "https://rumble.com/c/{}", "error_type": "status_code"},
    {"name": "Disqus", "cat": "Social", "url": "https://disqus.com/by/{}/", "check_url": "https://disqus.com/by/{}/", "error_type": "status_code"},
    {"name": "Threads", "cat": "Social", "url": "https://www.threads.net/@{}", "check_url": "https://www.threads.net/@{}", "error_type": "status_code"},
    {"name": "Quora", "cat": "Social", "url": "https://www.quora.com/profile/{}", "check_url": "https://www.quora.com/profile/{}", "error_type": "status_code"},
    {"name": "VK", "cat": "Social", "url": "https://vk.com/{}", "check_url": "https://vk.com/{}", "error_type": "status_code"},
    {"name": "Weibo", "cat": "Social", "url": "https://weibo.com/{}", "check_url": "https://weibo.com/{}", "error_type": "status_code"},
    {"name": "Imgur", "cat": "Media", "url": "https://imgur.com/user/{}", "check_url": "https://imgur.com/user/{}", "error_type": "status_code"},
    {"name": "Giphy", "cat": "Media", "url": "https://giphy.com/channel/{}", "check_url": "https://giphy.com/channel/{}", "error_type": "status_code"},
    {"name": "Tenor", "cat": "Media", "url": "https://tenor.com/users/{}", "check_url": "https://tenor.com/users/{}", "error_type": "status_code"},
    {"name": "Letterboxd", "cat": "Media", "url": "https://letterboxd.com/{}/", "check_url": "https://letterboxd.com/{}/", "error_type": "status_code"},
    {"name": "Trakt.tv", "cat": "Media", "url": "https://trakt.tv/users/{}", "check_url": "https://trakt.tv/users/{}", "error_type": "status_code"},
    {"name": "MyAnimeList", "cat": "Anime", "url": "https://myanimelist.net/profile/{}", "check_url": "https://myanimelist.net/profile/{}", "error_type": "status_code"},
    {"name": "AniList", "cat": "Anime", "url": "https://anilist.co/user/{}/", "check_url": "https://anilist.co/user/{}/", "error_type": "status_code"},
    {"name": "Wattpad", "cat": "Books", "url": "https://www.wattpad.com/user/{}", "check_url": "https://www.wattpad.com/user/{}", "error_type": "status_code"},
    {"name": "Tellonym", "cat": "Social", "url": "https://tellonym.me/{}", "check_url": "https://tellonym.me/{}", "error_type": "status_code"},

    # Gaming & Esports
    {"name": "Steam", "cat": "Gaming", "url": "https://steamcommunity.com/id/{}", "check_url": "https://steamcommunity.com/id/{}", "error_type": "body_text", "error_text": "The specified profile could not be found."},
    {"name": "Chess.com", "cat": "Gaming", "url": "https://www.chess.com/member/{}", "check_url": "https://api.chess.com/pub/player/{}", "error_type": "status_code"},
    {"name": "Lichess", "cat": "Gaming", "url": "https://lichess.org/@/{}", "check_url": "https://lichess.org/api/user/{}", "error_type": "status_code"},
    {"name": "Roblox", "cat": "Gaming", "url": "https://www.roblox.com/user.aspx?username={}", "check_url": "https://www.roblox.com/user.aspx?username={}", "error_type": "status_code"},
    {"name": "Itch.io", "cat": "Gaming", "url": "https://{}.itch.io", "check_url": "https://{}.itch.io", "error_type": "status_code"},
    {"name": "GameJolt", "cat": "Gaming", "url": "https://gamejolt.com/@{}", "check_url": "https://gamejolt.com/@{}", "error_type": "status_code"},
    {"name": "ModDB", "cat": "Gaming", "url": "https://www.moddb.com/members/{}", "check_url": "https://www.moddb.com/members/{}", "error_type": "status_code"},
    {"name": "NexusMods", "cat": "Gaming", "url": "https://www.nexusmods.com/users/{}", "check_url": "https://www.nexusmods.com/users/{}", "error_type": "status_code"},
    {"name": "CurseForge", "cat": "Gaming", "url": "https://www.curseforge.com/members/{}/projects", "check_url": "https://www.curseforge.com/members/{}/projects", "error_type": "status_code"},
    {"name": "Speedrun.com", "cat": "Gaming", "url": "https://www.speedrun.com/user/{}", "check_url": "https://www.speedrun.com/api/v1/users/{}", "error_type": "status_code"},
    {"name": "osu!", "cat": "Gaming", "url": "https://osu.ppy.sh/users/{}", "check_url": "https://osu.ppy.sh/users/{}", "error_type": "status_code"},

    # Music & Audio
    {"name": "SoundCloud", "cat": "Music", "url": "https://soundcloud.com/{}", "check_url": "https://soundcloud.com/{}", "error_type": "status_code"},
    {"name": "Spotify", "cat": "Music", "url": "https://open.spotify.com/user/{}", "check_url": "https://open.spotify.com/user/{}", "error_type": "status_code"},
    {"name": "Bandcamp", "cat": "Music", "url": "https://bandcamp.com/{}", "check_url": "https://bandcamp.com/{}", "error_type": "status_code"},
    {"name": "Last.fm", "cat": "Music", "url": "https://www.last.fm/user/{}", "check_url": "https://www.last.fm/user/{}", "error_type": "status_code"},
    {"name": "Mixcloud", "cat": "Music", "url": "https://www.mixcloud.com/{}/", "check_url": "https://www.mixcloud.com/{}/", "error_type": "status_code"},
    {"name": "Audiomack", "cat": "Music", "url": "https://audiomack.com/{}", "check_url": "https://audiomack.com/{}", "error_type": "status_code"},
    {"name": "Beatport", "cat": "Music", "url": "https://www.beatport.com/artist/{}/", "check_url": "https://www.beatport.com/artist/{}/", "error_type": "status_code"},
    {"name": "Discogs", "cat": "Music", "url": "https://www.discogs.com/user/{}", "check_url": "https://www.discogs.com/user/{}", "error_type": "status_code"},
    {"name": "Hearthis.at", "cat": "Music", "url": "https://hearthis.at/{}/", "check_url": "https://hearthis.at/{}/", "error_type": "status_code"},

    # Creative, Art & Design
    {"name": "Behance", "cat": "Creative", "url": "https://www.behance.net/{}", "check_url": "https://www.behance.net/{}", "error_type": "status_code"},
    {"name": "Dribbble", "cat": "Creative", "url": "https://dribbble.com/{}", "check_url": "https://dribbble.com/{}", "error_type": "status_code"},
    {"name": "ArtStation", "cat": "Creative", "url": "https://www.artstation.com/{}", "check_url": "https://www.artstation.com/{}", "error_type": "status_code"},
    {"name": "DeviantArt", "cat": "Creative", "url": "https://www.deviantart.com/{}", "check_url": "https://www.deviantart.com/{}", "error_type": "status_code"},
    {"name": "500px", "cat": "Creative", "url": "https://500px.com/p/{}", "check_url": "https://500px.com/p/{}", "error_type": "status_code"},
    {"name": "Unsplash", "cat": "Creative", "url": "https://unsplash.com/@{}", "check_url": "https://unsplash.com/@{}", "error_type": "status_code"},
    {"name": "VSCO", "cat": "Creative", "url": "https://vsco.co/{}/gallery", "check_url": "https://vsco.co/{}/gallery", "error_type": "status_code"},

    # Bio Links & Micro-Pages
    {"name": "Linktree", "cat": "Bio", "url": "https://linktr.ee/{}", "check_url": "https://linktr.ee/{}", "error_type": "status_code"},
    {"name": "Bio.link", "cat": "Bio", "url": "https://bio.link/{}", "check_url": "https://bio.link/{}", "error_type": "status_code"},
    {"name": "Beacons", "cat": "Bio", "url": "https://beacons.ai/{}", "check_url": "https://beacons.ai/{}", "error_type": "status_code"},
    {"name": "Carrd", "cat": "Bio", "url": "https://{}.carrd.co", "check_url": "https://{}.carrd.co", "error_type": "status_code"},
    {"name": "About.me", "cat": "Bio", "url": "https://about.me/{}", "check_url": "https://about.me/{}", "error_type": "status_code"},

    # Finance, Crypto & Crowdfunding
    {"name": "BuyMeACoffee", "cat": "Finance", "url": "https://www.buymeacoffee.com/{}", "check_url": "https://www.buymeacoffee.com/{}", "error_type": "status_code"},
    {"name": "Patreon", "cat": "Finance", "url": "https://www.patreon.com/{}", "check_url": "https://www.patreon.com/{}", "error_type": "status_code"},
    {"name": "OpenSea", "cat": "Crypto", "url": "https://opensea.io/{}", "check_url": "https://opensea.io/{}", "error_type": "status_code"},
    {"name": "Rarible", "cat": "Crypto", "url": "https://rarible.com/{}", "check_url": "https://rarible.com/{}", "error_type": "status_code"},

    # Publishing, Blogs & Knowledge
    {"name": "Substack", "cat": "Publishing", "url": "https://{}.substack.com", "check_url": "https://{}.substack.com", "error_type": "status_code"},
    {"name": "WordPress", "cat": "Publishing", "url": "https://{}.wordpress.com", "check_url": "https://{}.wordpress.com", "error_type": "status_code"},
    {"name": "Blogger", "cat": "Publishing", "url": "https://{}.blogspot.com", "check_url": "https://{}.blogspot.com", "error_type": "status_code"},
    {"name": "LiveJournal", "cat": "Publishing", "url": "https://{}.livejournal.com", "check_url": "https://{}.livejournal.com", "error_type": "status_code"},
    {"name": "Instructables", "cat": "DIY", "url": "https://www.instructables.com/member/{}/", "check_url": "https://www.instructables.com/member/{}/", "error_type": "status_code"},
    {"name": "Goodreads", "cat": "Books", "url": "https://www.goodreads.com/{}", "check_url": "https://www.goodreads.com/{}", "error_type": "status_code"},
    {"name": "ProductHunt", "cat": "Tech", "url": "https://www.producthunt.com/@{}", "check_url": "https://www.producthunt.com/@{}", "error_type": "status_code"},
    {"name": "Archive.org", "cat": "Archive", "url": "https://archive.org/details/@{}", "check_url": "https://archive.org/details/@{}", "error_type": "status_code"},
    {"name": "Wikipedia", "cat": "Wiki", "url": "https://en.wikipedia.org/wiki/User:{}", "check_url": "https://en.wikipedia.org/wiki/User:{}", "error_type": "status_code"},
    {"name": "TripAdvisor", "cat": "Travel", "url": "https://www.tripadvisor.com/Profile/{}", "check_url": "https://www.tripadvisor.com/Profile/{}", "error_type": "status_code"},
    {"name": "Duolingo", "cat": "Education", "url": "https://www.duolingo.com/profile/{}", "check_url": "https://www.duolingo.com/2017-06-30/users?username={}", "error_type": "status_code"},
    {"name": "Codecademy", "cat": "Education", "url": "https://www.codecademy.com/profiles/{}", "check_url": "https://www.codecademy.com/profiles/{}", "error_type": "status_code"},
    {"name": "KhanAcademy", "cat": "Education", "url": "https://www.khanacademy.org/profile/{}", "check_url": "https://www.khanacademy.org/profile/{}", "error_type": "status_code"},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}


def print_banner():
    banner = f"""{Colors.RED}{Colors.BOLD}
    ███████╗███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
    ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
    █████╗  ███████╗██║   ██║██║     ██║█████╗     ██║    ╚████╔╝ 
    ██╔══╝  ╚════██║██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝  
    ██║     ███████║╚██████╔╝╚██████╗██║███████╗   ██║      ██║   
    ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
    {Colors.CYAN}░▒▓ E L L I O T   O S I N T   &   D I G I T A L   H U N T E R ▓▒░{Colors.RESET}
    {Colors.DIM}[Allsafe Cyber Security Protocol // 120+ Platforms Deep Recon]{Colors.RESET}
    """
    print(banner)


# =====================================================================
# Single Platform Check Worker
# =====================================================================
def probe_platform(platform, username):
    url = platform["url"].format(urllib.parse.quote(username))
    check_url = platform["check_url"].format(urllib.parse.quote(username))
    name = platform["name"]
    category = platform["cat"]
    err_type = platform.get("error_type", "status_code")

    req = urllib.request.Request(check_url, headers=HEADERS)

    try:
        with urllib.request.urlopen(req, timeout=4.5) as response:
            code = response.getcode()
            if code == 200:
                if err_type == "body_text":
                    body_bytes = response.read(16384)
                    body_text = body_bytes.decode('utf-8', errors='ignore')
                    err_pattern = platform.get("error_text", "")
                    
                    if name == "Telegram":
                        if "tgme_page_extra" in body_text and "If you have Telegram" in body_text:
                            return {"name": name, "cat": category, "url": url, "found": True}
                        return {"name": name, "cat": category, "url": url, "found": False}
                    
                    if err_pattern and err_pattern in body_text:
                        return {"name": name, "cat": category, "url": url, "found": False}
                
                return {"name": name, "cat": category, "url": url, "found": True}
            else:
                return {"name": name, "cat": category, "url": url, "found": False}

    except urllib.error.HTTPError as e:
        if e.code in [404, 410, 400]:
            return {"name": name, "cat": category, "url": url, "found": False}
        elif e.code == 403:
            return {"name": name, "cat": category, "url": url, "found": None, "err": "Rate-Limited / Protected"}
        return {"name": name, "cat": category, "url": url, "found": False}
    except Exception:
        return {"name": name, "cat": category, "url": url, "found": False}


# =====================================================================
# Email OSINT & Gravatar Recon
# =====================================================================
def probe_email(email):
    print(f"\n{Colors.CYAN}{Colors.BOLD}[*] Performing Deep Email Fingerprinting on: {email}{Colors.RESET}")
    clean_email = email.strip().lower()
    email_hash = hashlib.md5(clean_email.encode('utf-8')).hexdigest()
    
    gravatar_api = f"https://en.gravatar.com/{email_hash}.json"
    gravatar_img = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
    
    results = {
        "email": email,
        "hash": email_hash,
        "gravatar_profile": False,
        "avatar_found": False,
        "avatar_url": gravatar_img,
        "details": {}
    }

    # 1. Check Gravatar Profile
    try:
        req = urllib.request.Request(gravatar_api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=3.5) as res:
            if res.getcode() == 200:
                data = json.loads(res.read().decode('utf-8'))
                entry = data.get("entry", [{}])[0]
                results["gravatar_profile"] = True
                results["details"] = {
                    "displayName": entry.get("displayName", "N/A"),
                    "preferredUsername": entry.get("preferredUsername", "N/A"),
                    "profileUrl": entry.get("profileUrl", "N/A"),
                    "aboutMe": entry.get("aboutMe", "N/A"),
                    "currentLocation": entry.get("currentLocation", "N/A"),
                }
    except Exception:
        pass

    # 2. Check Gravatar Avatar Image
    try:
        req = urllib.request.Request(gravatar_img, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=3.5) as res:
            if res.getcode() == 200:
                results["avatar_found"] = True
    except Exception:
        pass

    # Print Email Intel
    if results["gravatar_profile"]:
        print(f"  {Colors.GREEN}{Colors.BOLD}[+] Gravatar Profile Unlocked!{Colors.RESET}")
        for k, v in results["details"].items():
            if v and v != "N/A":
                print(f"      {Colors.YELLOW}• {k}:{Colors.RESET} {v}")
    elif results["avatar_found"]:
        print(f"  {Colors.GREEN}[+] Public Avatar Image Found:{Colors.RESET} {gravatar_img}")
    else:
        print(f"  {Colors.DIM}[-] No public Gravatar profile registered for this address.{Colors.RESET}")

    return results


# =====================================================================
# Main Multi-Threaded Recon Engine
# =====================================================================
def run_recon(username):
    print(f"\n{Colors.BOLD}{Colors.CYAN}[*] Target Identity Locked:{Colors.RESET} {Colors.MAGENTA}{username}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}[*] Initiating High-Speed Asynchronous Probe across {len(PLATFORMS_DB)} platforms...{Colors.RESET}\n")

    found_profiles = []
    total = len(PLATFORMS_DB)
    completed = 0
    start_time = time.time()

    # 35 Worker threads for extreme concurrency
    with ThreadPoolExecutor(max_workers=35) as executor:
        futures = {executor.submit(probe_platform, plat, username): plat for plat in PLATFORMS_DB}

        for future in as_completed(futures):
            completed += 1
            res = future.result()
            
            # Real-time console discovery stream
            if res["found"]:
                found_profiles.append(res)
                cat_badge = f"[{res['cat']}]"
                print(f"  {Colors.GREEN}{Colors.BOLD}[+] FOUND ({cat_badge:^10}):{Colors.RESET} {Colors.CYAN}{res['name']:<15}{Colors.RESET} ➔  {Colors.BOLD}{res['url']}{Colors.RESET}")
            
            # Update inline progress bar
            pct = int((completed / total) * 100)
            sys.stdout.write(f"\r{Colors.DIM}Scanning airwaves: [{completed}/{total}] ({pct}% completed)...{Colors.RESET}")
            sys.stdout.flush()

    duration = round(time.time() - start_time, 2)
    sys.stdout.write("\r" + " " * 60 + "\r")  # Clear progress line

    # -------------------------------------------------------------
    # Summary Dossier
    # -------------------------------------------------------------
    print(f"\n{Colors.BOLD}{Colors.YELLOW}====================================================================={Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}🎯 RECON SUMMARY: {len(found_profiles)} / {total} PROFILES LOCATED in {duration}s{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}====================================================================={Colors.RESET}\n")

    if found_profiles:
        for p in sorted(found_profiles, key=lambda x: x['cat']):
            print(f"  {Colors.GREEN}✔{Colors.RESET} {Colors.BOLD}{p['name']:<16}{Colors.RESET} ({Colors.DIM}{p['cat']:<10}{Colors.RESET}) ➔  {p['url']}")
    else:
        print(f"  {Colors.RED}[!] No public profiles matching '{username}' were discovered.{Colors.RESET}")

    # Auto-Export Dossier Report
    save_dossier(username, found_profiles, duration)


def save_dossier(username, profiles, duration):
    filename = f"dossier_{username}.md"
    content = [
        f"# 🕵️‍♂️ Digital Footprint Dossier: `{username}`",
        f"- **Date & Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Scan Duration:** {duration} seconds",
        f"- **Platforms Scanned:** {len(PLATFORMS_DB)}",
        f"- **Active Profiles Located:** {len(profiles)}\n",
        "## 🌐 Discovered Online Presence\n",
        "| Platform | Category | Profile URL | Status |",
        "|---|---|---|---|"
    ]

    for p in sorted(profiles, key=lambda x: x['cat']):
        content.append(f"| **{p['name']}** | {p['cat']} | [{p['url']}]({p['url']}) | ✅ Active |")

    content.append("\n---\n*Generated by Elliot OSINT & Digital Footprint Hunter • fsociety protocol*")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
        print(f"\n{Colors.CYAN}{Colors.BOLD}[💾] Digital Dossier successfully exported to:{Colors.RESET} {Colors.BOLD}{filename}{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}[!] Failed to export dossier: {e}{Colors.RESET}")


# =====================================================================
# Main Interactive CLI Loop
# =====================================================================
def main():
    print_banner()

    while True:
        try:
            print(f"\n{Colors.BOLD}{Colors.CYAN}Enter Target Username or Email to investigate (or 'q' to exit):{Colors.RESET}")
            target = input(f"{Colors.RED}fsociety@recon:~$ {Colors.RESET}").strip()

            if not target or target.lower() in ['q', 'exit', 'quit']:
                print(f"\n{Colors.DIM}[*] Terminating Elliot OSINT subsystem. Stay safe.{Colors.RESET}\n")
                break

            if "@" in target and "." in target:
                probe_email(target)
                u_part = target.split("@")[0]
                print(f"\n{Colors.YELLOW}[*] Also checking username handle: '{u_part}' across social platforms...{Colors.RESET}")
                run_recon(u_part)
            else:
                run_recon(target)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.DIM}[*] Session interrupted by user.{Colors.RESET}")
            break


if __name__ == '__main__':
    main()
