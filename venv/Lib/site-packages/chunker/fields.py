import os
import struct


class Field(object):
    """
    Base field class.

    It's abstract and cannot be used directly.

    :param name: Field name.
    """
    def __init__(self, name):
        self.name = name
        self.value = None
        self.length = 0

    def populate(self, fp, chunk):
        """
        Populate this field.

        You should override this or it will raise :exc:`NotImplementedError`.
        """
        raise NotImplementedError('Field is abstract.')


class BytesField(Field):
    """
    Base class for fixed length fields.

    It reads fixed count of bytes and decode them using :meth:`struct.unpack`.

    :param name: Field name.
    :param fmt: Format to be passed to :meth:`struct.unpack`.
    :param length: Field length in bytes.
    """
    def __init__(self, name, fmt, length):
        super(BytesField, self).__init__(name)
        self.name = name
        self.fmt = fmt
        self.length = length

    def populate(self, fp, chunk):
        buf = fp.read(self.length)
        self.value = struct.unpack(self.fmt, buf)[0]


class UnsignedLongField(BytesField):
    """
    Read 4 bytes and convert them into an unsigned long value.

    :param name: Field name.
    :param big_endian: If should be decoded in big-endian bytes order. Default is :const:`False`.
    """
    def __init__(self, name, big_endian=False):
        endian = '>' if big_endian else '<'
        fmt = endian + 'L'
        super(UnsignedLongField, self).__init__(name, fmt, 4)


class UnsignedShortField(BytesField):
    """
    Read 2 bytes and convert them into an unsigned short value.

    :param name: Field name.
    :param big_endian: If should be decoded in big-endian bytes order. Default is :const:`False`.
    """
    def __init__(self, name, big_endian=False):
        endian = '>' if big_endian else '<'
        fmt = endian + 'H'
        super(UnsignedShortField, self).__init__(name, fmt, 2)


class UnsignedCharField(BytesField):
    """
    Read 1 byte and convert them into an unsigned char value.

    :param name: Field name.
    :param big_endian: If should be decoded in big-endian bytes order. Default is :const:`False`.
    """
    def __init__(self, name, big_endian=False):
        endian = '>' if big_endian else '<'
        fmt = endian + 'B'
        super(UnsignedCharField, self).__init__(name, fmt, 1)


class VariableLengthField(Field):
    """
    Base class for field with variable length. Its length is based on another field.

    When populating, it simply read length and doesn't move on :obj:`fp` or read any data.

    :param name: Field name.
    :param length_field_name: Field name in the same chunk indicating the length of this field.
    """
    def __init__(self, name, length_field_name):
        super(VariableLengthField, self).__init__(name)
        self.length_field_name = length_field_name

    def populate(self, fp, chunk):
        self.length = chunk.__getattr__(self.length_field_name)


class StringField(VariableLengthField):
    """
    Read data with variable length. Its length is based on another field.

    :param name: Field name.
    :param length_field_name: Field name in the same chunk indicating the length of this field.
    """
    def populate(self, fp, chunk):
        super(StringField, self).populate(fp, chunk)
        self.value = fp.read(self.length)


class SkipBasedOnLengthField(VariableLengthField):
    """
    Skip data with variable length. Its length is based on another field.

    :param name: Field name.
    :param length_field_name: Field name in the same chunk indicating the length of this field.
    """
    def populate(self, fp, chunk):
        super(SkipBasedOnLengthField, self).populate(fp, chunk)
        fp.seek(self.length, os.SEEK_CUR)


class SkipBasedOnCalcField(Field):
    """
    Skip data with variable length. Its length is calculated from :func:`calc_func`.

    :param name: Field name.
    :param calc_func: Function to calculate the length to skip. When populating, this :obj:`chunk` will be passed to it as a parameter.

    Example::

        Fields = (
            UnsignedLongField('data_length'),
            SkipBasedOnCalcField('skip', lambda c: 3 * c.data_length),
        )
    """
    def __init__(self, name, calc_func):
        super(SkipBasedOnCalcField, self).__init__(name)
        self.calc_func = calc_func

    def populate(self, fp, chunk):
        offset = self.calc_func(chunk)
        fp.seek(offset, os.SEEK_CUR)


class SkipToTheEndField(Field):
    """
    Skip data to the end.

    The end depends on :attr:`fp.total_length`.

    :param name: Field name.
    """
    def populate(self, fp, chunk):
        if chunk.parser is not None:
            fp.seek(0, os.SEEK_END)
        else:
            raise AttributeError('No parser is provided')
