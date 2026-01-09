[![Bandit](https://github.com/018929014/pyxdcc-cli/actions/workflows/bandit.yml/badge.svg)](https://github.com/018929014/pyxdcc-cli/actions/workflows/bandit.yml)
[![Build Windows EXE](https://github.com/018929014/pyxdcc-cli/actions/workflows/build-exe.yml/badge.svg)](https://github.com/018929014/pyxdcc-cli/actions/workflows/build-exe.yml)
[![CodeQL](https://github.com/018929014/pyxdcc-cli/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/018929014/pyxdcc-cli/actions/workflows/github-code-scanning/codeql)
## ⚠️ Changes from Parent Version

This fork includes the following changes:

- **Removed dependency to mpv and fzf** : I use mpv but some people might still use vlc or other media player, I don't want to install fzf on my machine
- **IPv6 Rejection**: Automatically detects and rejects IPv6-only XDCC bots to avoid connection failures on IPv4-only networks
- **Bot Name Filtering**: Displays bot names in the selection menu and filters out known IPv6-only bots (CR-HOLLAND-IPv6, CR-ARUTHA-IPv6, XDCC|IPv6, etc.)
- **Enhanced Progress Display**: Colored progress bar with real-time download speed and percentage
- **CI/CD Integration**: Added GitHub Actions workflow to automatically build Windows EXE releases on git tags

Don't blame me for this repo, I just wanted to make something for myself and share it with the community.
It doesn't respect any golden standard in terms of git flow and is a mess but at least it exist.
If you want to get serious, well, consider using go instead lol


pyxdcc-cli
=====

#### A cli interface for watching anime from xdcc inspired by [ani-cli](https://github.com/pystardust/ani-cli).

### Compatibility

- Python 3.11+
- Tested only on Windows
- Automatic Windows EXE builds via GitHub Actions

Requirements
------------

* Python 3.11+
* [mpv](https://github.com/mpv-player/mpv)
* [fzf](https://github.com/junegunn/fzf)

Both mpv and fzf must be available on PATH.

Installation
------------

    pip install pyxdcc-cli

Usage
-----

Run the following to launch the interactive prompt.

    $ xdcc-cli
