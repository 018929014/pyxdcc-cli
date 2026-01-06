pyxdcc-cli
=====

#### A cli interface for watching anime from xdcc inspired by [ani-cli](https://github.com/pystardust/ani-cli).

## Changes from Parent Version

This fork includes the following changes:

- **Removed dependency to mpv and fzf** : I use mpv but some people might still use vlc or other media player, I don't want to install fzf on my machine
- **IPv6 Rejection**: Automatically detects and rejects IPv6-only XDCC bots to avoid connection failures on IPv4-only networks
- **Bot Name Filtering**: Displays bot names in the selection menu and filters out known IPv6-only bots (CR-HOLLAND-IPv6, CR-ARUTHA-IPv6, XDCC|IPv6, etc.)
- **Enhanced Progress Display**: Colored progress bar with real-time download speed and percentage
- **CI/CD Integration**: Added GitHub Actions workflow to automatically build Windows EXE releases on git tags


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