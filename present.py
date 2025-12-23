import argparse
import subprocess
import threading
import os
import time
import logging
import signal

logger = logging.getLogger(__name__)

ev_stop_showing_img: threading.Event = threading.Event()
ev_stop_program: threading.Event = threading.Event()


def catch_sigint(sig, frame):
    logger.info("Exiting")
    ev_stop_program.set()
    ev_stop_showing_img.set()

# TODO: catch keyboard interrupt
# TODO: try mpv with framebuffer, so we could also play videos?


class Config:
    def __init__(self, config_file: [str | None] = None):
        verbosity_level: int = 0
        self.n_webpages: int = 1
        self.n_photos: int = 3
        self.random: bool = False
        self.media: list = []
        self.viewer: str = "fbi"
        self.timeout: int = 10
        if not config_file:
            return
        # TODO: parse config file


presentation_config: Config = Config()


class MediaList:

    def __init__(self, show_in_a_row: int = 1, l_path: list[str] = None):
        """Set up a list of media (paths to files)

        Args:
            show_in_a_row (int, optional): show this many items from this media list in a row. Defaults to 1.
            l_path (list[str], optional):  List of paths to media files. Defaults to None.
                                           If none are provided you must add them later for the list to be useful
        """
        self._i_current: int = 0
        self._correct: bool = False
        self._l_path: list[str] = l_path
        self.n_show_in_a_row = show_in_a_row
        self._n_showed = 0
        if len(self._l_path) == 0:
            self._correct = False
        else:
            self._correct = True

    def get_next_media_path(self) -> str:
        """Return the path to the next media file.
        When called multiple times it will start at the beginning of the list.
        If the list is empty an empty path will be returned.

        Returns:
            str: path to the next media file
        """
        if not self._correct:
            return ""

        if self._i_current + 1 >= len(self._l_path):
            self._i_current = 0
        retval = self._l_path[self._i_current]
        self._i_current += 1
        self._n_showed += 1
        return retval

    def has_content(self) -> bool:
        """check if the MediaList has content

        Returns:
            bool: _description_
        """
        return len(self._l_path) > 0

    def is_my_turn(self) -> bool:
        if not self.has_content():
            return False
        if self._n_showed < self.n_show_in_a_row:
            return True
        else:
            self._n_showed = 0
            return False

    def reset_turn(self) -> None:
        self._n_showed = 0


class MediaListManager:

    def __init__(self):
        self._media_lists: list[MediaList] = []
        self._i_mlist: int = 0

    # reate a new MediaList from a path (directory or glob expression) + add it to the MediaListManager
    def add_media_list_from_path(self, path: str, show_this_many_in_a_row=1) -> None:
        if len(path) == 0:
            logger.warning("path empty")
            return
        l_media = [
            os.path.join(path, contents)
            for contents in os.listdir(path)
            if os.path.isfile(os.path.join(path, contents))
        ]
        media_list = MediaList(show_in_a_row=show_this_many_in_a_row, l_path=l_media)
        self._media_lists.append(media_list)

    def get_next_media(self) -> str:
        current_ml = self._get_next_ml()
        return current_ml.get_next_media_path()
    
    def _get_next_ml(self) -> [MediaList | None]:
        ml_len: int = len(self._media_lists)
        if ml_len == 0:
            return None
        
        ml = self._media_lists[self._i_mlist]
        if(ml.is_my_turn()):
            return ml
        else:
            if self._i_mlist + 1 >= ml_len:
                self._i_mlist = 0
                for ml in self._media_lists:
                    ml.reset_turn()
            else:
                self._i_mlist += 1
            ml = self._media_lists[self._i_mlist]
        return ml

    def is_there_something_to_show(self) -> bool:
        show: bool = False
        for ml in self._media_lists:
            if ml.has_content():
                show = True
                break
        return show


def present_content(path: str):
    """Runs framebuffer program to present content refered to by 'path'"""
    viewer = subprocess.Popen(f"exec {presentation_config.viewer} {path}", shell=True)
    ev_stop_showing_img.wait()
    #os.kill(viewer.pid, signal.SIGKILL) 
    viewer.terminate()
    #viewer.kill()


def run_slideshow():
    """Controls the slideshow flow"""
    ml_manager: MediaListManager = MediaListManager()
    for m in presentation_config.media:
        ml_manager.add_media_list_from_path(m[0], int(m[1]))

    if not ml_manager.is_there_something_to_show():
        print("no files to show")
        return

    while not ev_stop_program.is_set():
        file: str = ""
        file = ml_manager.get_next_media()

        th_show_image = threading.Thread(target=present_content, args=[file])
        th_show_image.start()
        ev_stop_program.wait(timeout=presentation_config.timeout)
        #th_show_image.join()
        ev_stop_showing_img.set()
        ev_stop_showing_img.clear()
    # endwhile


def main():
    """Main entry point"""

    signal.signal(signal.SIGINT, catch_sigint)

    parser = argparse.ArgumentParser(description="Present rnadom images + webpages uing fbi")
    parser.add_argument("-v", "--verbose", type=int, dest="verbose", help="verbosity level")
    parser.add_argument("-c", "--config", type=str, dest="config", help="config file")
    parser.add_argument(
        "-m",
        "--media",
        action="append",
        dest="media",
        nargs="+",
        help="[media directory] (n)   n: show n media files from this dir consecutively",
    )
    parser.add_argument(
        "--viewer",
        type=str,
        dest="viewer",
        help="name of / path to the image viewer to use",
    )
    parser.add_argument("-t", "--timeout", type=int, dest="timeout", help="how long to show each media file")

    args = parser.parse_args()

    config_file: str = ""

    if args.config:
        config_file = str(args.config)
        # TODO: check if config file exists
        presentation_config.__init__(config_file=config_file)

    if args.verbose:
        presentation_config.verbosity_level = args.verbose

    if args.media:
        media = args.media
        if (len(media) > 0):
            for m in media:
                if(not len(m) == 2):
                    logger.error("Expecting argument to be of format <path> <n>")
                    ev_stop_program.set()
                    break
        if not ev_stop_program.is_set():
            presentation_config.media = args.media

    if args.viewer:
        presentation_config.viewer = str(args.viewer)
    
    if args.timeout:
        presentation_config.timeout = int(args.timeout)

    run_slideshow()


if __name__ == "__main__":
    main()
