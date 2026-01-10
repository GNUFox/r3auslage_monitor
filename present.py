import subprocess
import threading
import os
import time
import logging
from python_mpv_jsonipc import MPV
import configparser

from media import MediaListManager, MediaList

logger = logging.getLogger(__name__)

ev_stop_showing_img: threading.Event = threading.Event()
ev_stop_program: threading.Event = threading.Event()


class Config:
    def __init__(self, config_file: [str | None] = None):
        self.media_show_time: int = 2
        self.viewer: str = "mpv --loop --ao=null"
        self.random: bool = False
        self.verbosity_level: int = 0

        self.media: list[dict] = []

        self.mpv_ipc_socket: str = "/tmp/mpv-socket"
        self.mpv: MPV

        if not config_file:
            return
        # TODO: parse config file
        if not os.path.isfile(config_file):
            logging.critical(f"config file '{config_file}' does not exists, using defaults")
            return

        config = configparser.ConfigParser()
        config.read(config_file)

        # BASIC config
        if "BASIC" not in config:
            logger.warn("Missing BASIC section in config file, using defaults")
        else:
            BASIC = config["BASIC"]
            if "media_show_time" in BASIC:
                self.media_show_time = int(BASIC["media_show_time"])
            if "mpv_options" in BASIC:
                self.mpv_options = BASIC["mpv_options"]
            if "random" in BASIC:
                self.random = bool(BASIC["random"])
            if "verbosity_level" in BASIC:
                self.verbosity_level = int(BASIC["verbosity_level"])

        # Media sections
        for config_section in config:
            if config_section.startswith("media"):
                media_section = config[config_section]
                path = ""
                show_in_a_row = 1
                run_script = ""
                if "path" in media_section:
                    path = str(media_section["path"])
                if "show_in_a_row" in media_section:
                    show_in_a_row = int(media_section["show_in_a_row"])
                if "run_script" in media_section:
                    run_script = str(media_section["run_script"])

                self.add_media_from_cmd_line([[path, show_in_a_row, run_script]])

    def add_media_from_cmd_line(self, cmdline_media):
        for m in cmdline_media:
            if len(m) <= 3 and len(m) >= 1:
                self.media.append(self._get_media_dict(m))
            else:
                logging.warn(f"commandline argument {m} number of entries does not match, must be 1 to 3, see help")

    def _get_media_dict(self, cmdline_media_entry):
        md = dict()
        md["path"] = cmdline_media_entry[0]
        md["show_in_row"] = 1
        md["run_script"] = ""
        if len(cmdline_media_entry) >= 2:
            md["show_in_row"] = int(cmdline_media_entry[1])
        if len(cmdline_media_entry) >= 3:
            md["run_script"] = cmdline_media_entry[2]
        return md


presentation_config: Config = Config()


def present_content(mpv: MPV, path: str):
    """Runs framebuffer program to present content refered to by 'path'"""
    # viewer = subprocess.Popen(f"exec {presentation_config.viewer} {path}", shell=True)
    # ev_stop_showing_img.wait()
    # os.kill(viewer.pid, signal.SIGKILL)
    # time.sleep(0.5)
    # viewer.terminate()
    # viewer.kill()
    mpv.play(path)


def run_slideshow():
    """Controls the slideshow flow"""
    ml_manager: MediaListManager = MediaListManager()
    for m in presentation_config.media:
        ml = MediaList(m["path"], m["show_in_row"], m["run_script"])
        ml_manager.add_media_list(ml)

    if not ml_manager.is_there_something_to_show():
        print("no files to show")
        return

    start_mpv_json_ipc_server()
    time.sleep(5)  # give mpv some time to start :(, hdd is slow
    mpv = MPV(start_mpv=False, ipc_socket="/tmp/mpv-socket")

    while not ev_stop_program.is_set():
        file: str = ""
        file = ml_manager.get_next_media()

        th_show_image = threading.Thread(target=present_content, args=[mpv, file])
        th_show_image.start()
        ev_stop_program.wait(timeout=presentation_config.media_show_time)
        # th_show_image.join()
        ev_stop_showing_img.set()
        ev_stop_showing_img.clear()
    # endwhile


def start_mpv_json_ipc_server():
    mpv = subprocess.Popen(
        f"exec {presentation_config.viewer} "
        "--input-ipc-server=/tmp/mpv-socket "
        "pixel.png", shell=True)
