import os
import logging

logger = logging.getLogger(__name__)


class Media:

    def __init__(self, path: str, run_function=None):
        self.path = path
        self.run_function = run_function


class MediaList:

    def __init__(self, path: str, show_in_a_row: int = 1, run_script: str = None):
        """Set up a list of media (paths to files)

        Args:
            show_in_a_row (int, optional): show this many items from this media list in a row. Defaults to 1.
            l_path (list[str], optional):  List of paths to media files. Defaults to None.
                                           If none are provided you must add them later for the list to be useful
        """
        self._i_current: int = 0
        self._correct: bool = False
        self._l_path: list[str] = []
        self.n_show_in_a_row = show_in_a_row
        self._n_showed = 0

        # TODO: check if path exists
        if len(path) == 0:
            logger.warning("path empty")
            self._correct = False
            return
        
        self._l_path = [
            os.path.join(path, contents)
            for contents in os.listdir(path)
            if os.path.isfile(os.path.join(path, contents))
        ]

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

        if self._i_current + 1 > len(self._l_path):
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

    def is_correct(self) -> bool:
        return self._correct


class MediaListManager:

    def __init__(self):
        self._media_lists: list[MediaList] = []
        self._i_mlist: int = 0

    # create a new MediaList from a path (directory or glob expression) + add it to the MediaListManager
    # def add_media_list_from_path(self, path: str, show_this_many_in_a_row=1) -> None:
    #    media_list = MediaList(show_in_a_row=show_this_many_in_a_row, l_path=l_media)
    #    self._media_lists.append(media_list)

    def add_media_list(self, ml: MediaList) -> None:
        if ml.is_correct():
            self._media_lists.append(ml)

    def get_next_media(self) -> str:
        current_ml = self._get_next_ml()
        if not current_ml:
            return "pixel.png"  # TODO: remove hardcoded paths, this is only for testing
        return current_ml.get_next_media_path()

    def _get_next_ml(self) -> [MediaList | None]:
        ml_len: int = len(self._media_lists)
        if ml_len == 0:
            return None

        ml = self._media_lists[self._i_mlist]
        if ml.is_my_turn():
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
