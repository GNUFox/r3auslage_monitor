import argparse
import subprocess
import threading
import os
import time

ev_stop_showing_img: threading.Event = threading.Event()


# TODO: catch keyboard interrupt
# TODO: try mpv with framebuffer, so we could also play videos?


class config:
    verbosity_level: int = 0
    n_webpages: int = 1
    n_photos: int = 3
    random: bool = False
    photos_dir: str = ""
    webpages_dir: str = ""
    viewer: str = "fbi"

    def __init__(self, config_file: [str | None] = None):
        if not config_file:
            return
        # TODO: parse config file


presentation_config: config = config()


def present_content(path: str):
    """Runs framebuffer program to present content refered to by 'path'"""
    # fbi = subprocess.Popen(["fbi", path])
    fbi = subprocess.Popen([presentation_config.viewer, path])
    ev_stop_showing_img.wait()
    fbi.terminate()


def run_slideshow():
    """Controls the slideshow flow"""
    l_webpages: list[str] = []
    l_photos: list[str] = []

    if presentation_config.webpages_dir:
        l_webpages = [
            os.path.join(presentation_config.webpages_dir, contents)
            for contents in os.listdir(presentation_config.webpages_dir)
            if os.path.isfile(os.path.join(presentation_config.webpages_dir, contents))
        ]
    if presentation_config.photos_dir:
        l_photos = [
            os.path.join(presentation_config.photos_dir, contents)
            for contents in os.listdir(presentation_config.photos_dir)
            if os.path.isfile(os.path.join(presentation_config.photos_dir, contents))
        ]

    if len(l_webpages) == 0:
        print("webpages dir is empty")
    if len(l_photos) == 0:
        print("photos dir is empty")
    if len(l_photos) == 0 and len(l_webpages) == 0:
        print("no files to show")
        return

    i_photo: int = 0
    i_webpage: int = 0
    b_webpage_presented: bool = True  # webpage = true
    while True:
        file: str = ""
        if i_photo + 1 == len(l_photos):
            i_photo = 0
        if i_webpage + 1 == len(l_webpages):
            i_webpage = 0

        if not i_photo % config.n_photos and not b_webpage_presented:
            # present webpage
            file = l_webpages[i_webpage]
            i_webpage += 1
            b_webpage_presented = True
        else:
            # prseent photo
            file = l_photos[i_photo]
            i_photo += 1
            b_webpage_presented = False

        th_show_image = threading.Thread(target=present_content, args=[file])
        th_show_image.start()
        time.sleep(2)
        ev_stop_showing_img.set()
        ev_stop_showing_img.clear()
    # endwhile


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(
        description="Present rnadom images + webpages uing fbi"
    )
    parser.add_argument(
        "-v", "--verbose", type=int, dest="verbose", help="verbosity level"
    )
    parser.add_argument("-c", "--config", type=str, dest="config", help="config file")
    parser.add_argument(
        "-p",
        "--photos",
        action="append",
        dest="photos",
        nargs="+",
        help="photos directory",
    )
    parser.add_argument(
        "-w",
        "--webpages",
        action="append",
        dest="webpages",
        nargs="+",
        help="webpages directory",
    )
    parser.add_argument(
        "--viewer",
        type=str,
        dest="viewer",
        help="name of / path to the image viewer to use",
    )

    parser.add_argument("--test-single-file", type=str, dest="single_file")

    args = parser.parse_args()

    config_file: str = ""

    if args.config:
        config_file = str(args.config)
        # TODO: check if config file exists
        presentation_config.__init__(config_file=config_file)

    if args.verbose:
        presentation_config.verbosity_level = args.verbose

    if args.photos:
        presentation_config.photos_dir = str(args.photos[0][0])  # TODO: handle list
    if args.webpages:
        presentation_config.webpages_dir = str(args.webpages[0][0])  # TODO: handle list

    if args.single_file:
        single_file = str(args.single_file)

    if args.viewer:
        presentation_config.viewer = str(args.viewer)

    run_slideshow()


if __name__ == "__main__":
    main()
