import argparse
import logging
import signal

from present import run_slideshow
from present import presentation_config, ev_stop_program, ev_stop_showing_img

logger = logging.getLogger(__name__)

def catch_sigint(sig, frame):
    """_summary_

    Args:
        sig (_type_): _description_
        frame (_type_): _description_
    """
    logger.info("Exiting")
    ev_stop_program.set()
    ev_stop_showing_img.set()

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
    parser.add_argument("-t", "--media_show_time", type=int, dest="media_show_time", help="how long to show each media file")

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
        if len(media) > 0:
            for m in media:
                if not (len(m) >= 2 and len(m) <= 3):
                    logger.error("Expecting argument to be of format <path> <n> [<script>]")
                    ev_stop_program.set()
                    break
        if not ev_stop_program.is_set():
            presentation_config.add_media_from_cmd_line(args.media)

    if args.viewer:
        presentation_config.viewer = str(args.viewer)

    if args.media_show_time:
        presentation_config.media_show_time = int(args.media_show_time)

    run_slideshow()


if __name__ == "__main__":
    main()
