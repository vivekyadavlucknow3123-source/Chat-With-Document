import os


class FilePtr:
    """
    A wrapper for file object to maintain some more states during parsing.

    - In file mode, :attr:`total_length` can be left None and will be read from
      file system.
    - In streaming mode, you **must** provide :attr:`total_length` to specify the
      end of the stream.

    :param fp: Original file object.
    :param total_length: Length of this.
    :param offset: Offset to the original file.
    """
    def __init__(self, fp, total_length=None, offset=0):
        self.fp = fp
        self.offset = offset
        if total_length is not None:
            self.total_length = total_length
        else:
            self.total_length = FilePtr.get_file_length(fp)

    @staticmethod
    def get_file_length(fp):
        """
        Get length of the file from local file system.
        """
        return os.fstat(fp.fileno()).st_size

    def read(self, n):
        """
        Read bytes.

        :param n: Count of bytes to read.
        :returns: Bytes.
        """
        return self.fp.read(n)

    def seek(self, pos, mode=os.SEEK_SET):
        """
        Seek position in sub file.

        :param pos: Position.
        :param mode: Seek mode.
        """
        if mode == os.SEEK_CUR:
            self.fp.seek(pos, os.SEEK_CUR)
        elif mode == os.SEEK_SET:
            self.fp.seek(self.offset + pos, os.SEEK_SET)
        elif mode == os.SEEK_END:
            self.fp.seek(self.offset + self.total_length + pos, os.SEEK_SET)

    def tell(self):
        """
        Current position in sub file.

        :returns: Current position.
        """
        return self.fp.tell() - self.offset

    def close(self):
        """
        Set internal references to None.

        Note that it will not close the original file object.
        """
        self.fp = None
        self.offset = 0
        self.total_length = 0

    def save_state(self):
        """
        Save internal state.
        """
        self._saved_pos = self.tell()

    def restore_state(self):
        """
        Restore last internal state.
        """
        self.seek(self._saved_pos, os.SEEK_SET)
