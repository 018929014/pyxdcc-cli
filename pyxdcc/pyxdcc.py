from xdcc_dl.pack_search import SearchEngines
from xdcc_dl.xdcc import XDCCClient
from tempfile import TemporaryDirectory
from multiprocessing import Process
from colorama import Fore, Style
import colorama
import time
import os
import sys


class SilencedXDCCClient(XDCCClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def progress_printer(self):
        pass


def prompt_selection(options, prompt_text="Select an option"):
    """Display a numbered menu and get user selection."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{prompt_text}{Style.RESET_ALL}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choice = int(input(f"{Fore.CYAN}{Style.BRIGHT}Enter number (1-{len(options)}): {Style.RESET_ALL}"))
            if 1 <= choice <= len(options):
                return choice - 1
            print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and {len(options)}.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")


def _download_process_worker(selected_result):
    """Worker function for downloading video. Must be at module level for multiprocessing."""
    client = SilencedXDCCClient(selected_result, channel_join_delay=3)
    client.download()


def download_video(search_results, tmp_dir):
    filtered_results = [result for result in search_results if "1080p" in result.filename]

    filenames = [result.filename.rsplit('.', 1)[0] for result in filtered_results]

    selected_index = prompt_selection(filenames, "Select a video to download:")
    selected_result = filtered_results[selected_index]

    selected_result.set_directory(tmp_dir)

    download = Process(target=_download_process_worker, args=(selected_result,))

    download.start()

    return selected_result, download


def play_video_file(file_path):
    """Play a video file using the system default player."""
    if sys.platform == "win32":
        os.startfile(file_path)
    elif sys.platform == "darwin":
        os.system(f"open '{file_path}'")
    else:
        os.system(f"xdg-open '{file_path}'")


def _play_video_worker(selected_result, tmp_dir):
    """Worker function for playing video. Must be at module level for multiprocessing."""
    file_path = os.path.join(tmp_dir, selected_result.filename)
    
    # Wait for file to exist
    while not os.path.exists(file_path):
        time.sleep(0.25)
    
    # Wait for file to be fully downloaded by checking if file size is stable
    last_size = 0
    stable_count = 0
    while stable_count < 5:  # Check 5 times that size hasn't changed
        try:
            current_size = os.path.getsize(file_path)
            if current_size == last_size:
                stable_count += 1
            else:
                stable_count = 0
            last_size = current_size
            time.sleep(0.5)
        except OSError:
            time.sleep(0.5)
    
    play_video_file(file_path)


def main():
    colorama.init(autoreset=True)

    print(Fore.BLUE + Style.BRIGHT + "Starting anime downloader...")

    with TemporaryDirectory(None, "xdcc-cli-") as tmp_dir:
        print(Fore.GREEN + Style.BRIGHT + f"Files will be downloaded to: {tmp_dir}" + Style.RESET_ALL)

        search_term = input(Fore.CYAN + Style.BRIGHT + "Enter search term: " + Style.RESET_ALL)
        search_results = SearchEngines.NIBL.value.search(search_term)
        selected_result, download = download_video(search_results, tmp_dir)
        choice = -1

        while True:
            if choice == 2:  # "Search again"
                search_term = input(Fore.CYAN + Style.BRIGHT + "Enter search term: " + Style.RESET_ALL)
                search_results = SearchEngines.NIBL.value.search(search_term)

            if choice == 1 or choice == 2:  # "Choose again" or "Search again"
                selected_result, download = download_video(search_results, tmp_dir)

            play = Process(target=_play_video_worker, args=(selected_result, tmp_dir))
            play.start()
            print(Fore.BLUE + Style.BRIGHT + "Download starting... Waiting for download to complete before playing...")
            download.join()
            print(Fore.GREEN + Style.BRIGHT + "Download complete! Starting playback...")
            play.join()

            choice = prompt_selection(
                ["Play again", "Choose again", "Search again", "Exit"],
                "What would you like to do?"
            )

            if choice != 0:  # Not "Play again"
                download.terminate()
                download.join()

            if choice == 3:  # "Exit"
                break


if __name__ == "__main__":
    main()
