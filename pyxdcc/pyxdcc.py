import multiprocessing
from xdcc_dl.pack_search import SearchEngines
from xdcc_dl.xdcc import XDCCClient
from tempfile import TemporaryDirectory
from multiprocessing import Process
from colorama import Fore, Style
import colorama
import time
import os
import sys
import logging
from irc.client import ServerConnection, Event


class SilencedXDCCClient(XDCCClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_ctcp(self, conn: ServerConnection, event: Event):
        """
        Override to reject IPv6 DCC offers.
        """
        if event.arguments[0] == "DCC":
            from xdcc_dl.xdcc.exceptions import UnrecoverableError
            import shlex
            
            payload = shlex.split(event.arguments[1])
            if payload[0] == "SEND":
                ip_str = payload[2]
                # Check if the IP is IPv6 (contains colons)
                if ':' in ip_str:
                    self.logger.warning(f"IPv6 bot detected ({ip_str}). Cancelling transfer and retrying...")
                    bot = event.source.split("!")[0]
                    # Cancel the current transfer
                    conn.privmsg(bot, "XDCC CANCEL")
                    # Request the pack again (bot might offer IPv4 next time)
                    raise UnrecoverableError()
        
        # Use parent's implementation for other cases
        super().on_ctcp(conn, event)

    # def download(self) -> str:
    #     """
    #     Override download to handle thread joining properly with IPv6 support.
    #     """
    #     error = False
    #     completed = False
    #     pause = 0
    #     message = ""

    #     try:
    #         self.logger.info(f"Connecting to "
    #                          f"{self.server.address}:{self.server.port} "
    #                          f"as user '{self.user.username}'")
    #         self.connect(
    #             self.server.address,
    #             self.server.port,
    #             self.user.username
    #         )

    #         self.logger.info(f"Delaying download initialization by "
    #                          f"{self.channel_join_delay}s")
    #         time.sleep(self.channel_join_delay)

    #         self.connected = True
    #         self.connect_start_time = time.time()

    #         self.timeout_watcher_thread.start()
    #         self.progress_printer_thread.start()

    #         self.start()
    #     except Exception as e:
    #         from xdcc_dl.xdcc.exceptions import (
    #             AlreadyDownloadedException, DownloadCompleted, 
    #             DownloadIncomplete, PackAlreadyRequested, UnrecoverableError
    #         )
            
    #         if isinstance(e, AlreadyDownloadedException):
    #             self.logger.warning("File already downloaded")
    #             completed = True
    #         elif isinstance(e, DownloadCompleted):
    #             message = f"File {self.pack.filename} downloaded successfully"
    #             completed = True
    #         elif isinstance(e, DownloadIncomplete):
    #             message = f"File {self.pack.filename} not downloaded successfully"
    #             completed = False
    #         elif isinstance(e, PackAlreadyRequested):
    #             message = "Pack already requested."
    #             completed = False
    #             pause = 60
    #         elif isinstance(e, UnrecoverableError):
    #             error = True
    #         else:
    #             raise
    #     finally:
    #         self.connected = False
    #         self.disconnected = True
    #         self.logger.info("Joining threads")
            
    #         # Only join threads that were actually started
    #         if self.timeout_watcher_thread.is_alive():
    #             self.timeout_watcher_thread.join()
    #         if self.progress_printer_thread.is_alive():
    #             self.progress_printer_thread.join()
    #         if self.ack_thread.is_alive():
    #             self.ack_thread.join()
            
    #         print("\n" + message)
    #         self.logger.info("Disconnecting")
    #         try:
    #             self._disconnect()
    #         except (Exception,):
    #             pass

    #     if error:
    #         self.logger.info("Aborting because of unrecoverable error")
    #         return "Failed"

    #     self.logger.debug("Pausing for {}s".format(pause))
    #     time.sleep(pause)

    #     if not completed:
    #         self.logger.warning("Download Incomplete. Retrying.")
    #         retry_client = SilencedXDCCClient(self.pack, True, self.timeout)
    #         retry_client.download_limit = self.download_limit
    #         retry_client.download()

    #     if not self.retry:
    #         dl_time = str(int(abs(time.time() - self.connect_start_time)))
    #         self.logger.info("Download completed in " + dl_time + " seconds.")

    #     return self.pack.get_filepath()

    def progress_printer(self):
        """Display download progress with colored output."""
        speed_progress = []
        while not self.downloading and not self.disconnected:
            pass
        time.sleep(1)

        printing = self.downloading and not self.disconnected
        while printing:
            printing = self.downloading and not self.disconnected

            speed_progress.append({
                "timestamp": time.time(),
                "progress": self.progress
            })
            while len(speed_progress) > 0 \
                    and time.time() - speed_progress[0]["timestamp"] > 7:
                speed_progress.pop(0)

            if len(speed_progress) > 0:
                bytes_delta = self.progress - speed_progress[0]["progress"]
                time_delta = time.time() - speed_progress[0]["timestamp"]
                if time_delta > 0:
                    ratio = int(bytes_delta / time_delta)
                    speed = f"{ratio / (1024*1024):.2f}MB/s"
                else:
                    speed = "0B/s"
            else:
                speed = "0B/s"

            percentage = (100 * (self.progress / self.filesize)) if self.filesize > 0 else 0
            bar_length = 40
            filled = int(bar_length * self.progress / self.filesize) if self.filesize > 0 else 0
            bar = "█" * filled + "░" * (bar_length - filled)

            log_message = f"\r{Fore.GREEN}{bar}{Style.RESET_ALL} {percentage:.1f}% | {self._format_size(self.progress)}/{self._format_size(self.filesize)} | {speed}"
            print(log_message, end="", flush=True)
            time.sleep(0.1)
    
    @staticmethod
    def _format_size(bytes_size):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}TB"


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
    # Configure logging to display xdcc_dl debug messages
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Ensure xdcc_dl loggers are visible
    logging.getLogger('xdcc_dl').setLevel(logging.DEBUG)
    logging.getLogger('xdcc_dl.xdcc').setLevel(logging.DEBUG)
    
    client = SilencedXDCCClient(selected_result, channel_join_delay=3)
    client.download()


def download_video(search_results, tmp_dir):
    # Bots known to only support IPv6 (add more as needed)
    ipv6_only_bots = {
        'CR-HOLLAND-IPv6|NEW',
        'CR-ARUTHA-IPv6|NEW',
        'XDCC|IPv6',
    }
    
    filtered_results = [result for result in search_results 
                       if "1080p" in result.filename and result.bot not in ipv6_only_bots]

    # Display results with bot names for filtering
    filenames = [f"{result.filename.rsplit('.', 1)[0]} ({result.bot})" for result in filtered_results]

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
    
    # Wait for file to exist (should be immediate since download is already done)
    max_wait = 30  # seconds
    elapsed = 0
    while not os.path.exists(file_path) and elapsed < max_wait:
        time.sleep(0.1)
        elapsed += 0.1
    
    if os.path.exists(file_path):
        play_video_file(file_path)
    else:
        print(Fore.RED + Style.BRIGHT + f"File not found: {file_path}" + Style.RESET_ALL)


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
    multiprocessing.freeze_support()
    main()
