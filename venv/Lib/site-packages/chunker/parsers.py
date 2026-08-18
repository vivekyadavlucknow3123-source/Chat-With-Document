import __future__

import os
import threading

from chunker.utils import FilePtr


class ParseTimeoutException(Exception):
    """
    Exception indicating that timeout occurs when parsing.
    """
    pass


class Parser(object):
    """
    Parse chunks from file or streaming.

    - In file mode, :attr:`total_length` can be left None and will be read from
      file system.
    - In streaming mode, you **must** provide :attr:`total_length` to specify the
      end of the stream.

    :param fp: File object to be read from.
    :param total_length: Total length of the source.
    :throws ParseTimeoutException: Timeout. Default is 60s.
    """
    ChunkClasses = ()
    Timeout = 60

    def __init__(self, fp, total_length=None):
        if isinstance(fp, FilePtr):
            self.fp = fp
        else:
            self.fp = FilePtr(fp, total_length)
        self.chunks = []
        self._timeout_timer = None
        self.is_timeout = False
        self.is_debug = False

    @staticmethod
    def get_file_length(fp):
        return os.fstat(fp.fileno()).st_size

    def parse(self):
        """
        Start parsing.

        If you want more debug info, call :meth:`enable_debug` before parsing.
        """
        self._set_timeout()

        while self.fp.tell() < self.fp.total_length:
            for chunk_cls in self.__class__.ChunkClasses:
                if chunk_cls.matches(self.fp):
                    chunk = chunk_cls(self.fp, self)
                    chunk.populate()
                    self.chunks.append(chunk)

                    if self.is_debug:
                        print(chunk)
                        print('Now at', hex(self.fp.tell()))
                    break

            if self.is_timeout:
                raise ParseTimeoutException()

        self._timeout_timer.cancel()

    def _set_timeout(self):
        def handler():
            self.is_timeout = True

        self._timeout_timer = threading.Timer(self.__class__.Timeout, handler)
        self._timeout_timer.start()

    def enable_debug(self):
        """
        Print debugging info when parsing.
        """
        self.is_debug = True

    def close(self):
        """
        Close the file object.
        """
        self.fp.close()


class FileParser(Parser):
    """
    Parse from file.

    :param path: File path.
    """
    def __init__(self, path):
        fp = open(path, 'rb')
        super(FileParser, self).__init__(fp)
