import __future__

import copy
import os


class Chunk(object):
    """
    Chunk in the file. A chunk usually contains a signature indicating its
    type, and a group of data fields.

    :param fp: File object to read from.
    :param parser: The parser it belongs to. It's optional and you can leave it None.

    To define your chunk class, you should follow these steps:

    1. Define its fields. Fields are populated in this order. See :doc:`fields` for more information.

    2. Define a :meth:`matches` or :meth:`safe_matches` class method to judge if the following bytes match this type of chunk.

        * Override :meth:`matches` to handle :attr:`fp` state by yourself.
        * Override :meth:`safe_matches` to get :attr:`fp` state auto saved.

    Example::

        import os
        import struct

        from chunker.chunks import Chunk

        class DataChunk(Chunk):
            Fields = (
                UnsignedLongField('sig'),   # 0x01020304
                UnsignedLongField('type'),
                UnsignedLongField('data_length'),
                StringField('data', length_field_name='data_length'),
            )

            @classmethod
            def safe_matches(fp):
                buf = fp.read(4)
                type = struct.unpack('>H', buf)[0]

                return type == 0x01020304

        if DataChunk.matches(fp):
            c = DataChunk(fp, None)
            print(c.data) # Access field value by its name
    """
    Fields = ()

    def __new__(cls, *args, **kargs):
        instance = super(Chunk, cls).__new__(cls)
        instance.fields = copy.deepcopy(cls.Fields)
        instance.fields_map = {f.name: f for f in instance.fields}
        return instance

    def __init__(self, fp, parser):
        self.fp = fp
        self.parser = parser

    def __getattr__(self, key):
        return self.fields_map[key].value

    @classmethod
    def matches(cls, fp):
        """
        Read next a few bytes to judge if the following data match this type
        of chunk.

        It calls :meth:`safe_matches` and restores :attr:`fp` state by default.

        You can override this to avoid saving :attr:`fp` state.

        :param fp: File object to read from.
        :returns: If the following bytes match this chunk type.
        """
        fp.save_state()
        matches = cls.safe_matches(fp)
        fp.restore_state()
        return matches

    @classmethod
    def safe_matches(cls, fp):
        """
        The difference between :meth:`safe_matches` and :meth:`matches` is that if you override this, you can get your :attr:`fp` state auto saved.

        You only need to override one of them:

        * Override :meth:`matches` to handle :attr:`fp` state by yourself.
        * Override :meth:`safe_matches` to get :attr:`fp` state auto saved.

        :param fp: File object to read from.
        :returns: If the following bytes match this chunk type.
        """
        return False

    def populate(self):
        """
        Populate chunk fields. After that, you can access each field data
        directly by field name.
        """
        for field in self.fields:
            field.populate(self.fp, self)
            # if self.parser is not None and self.parser.is_debug:
            #     print('%s: %s @ %s' % (
            #         field.name, field.value, hex(self.fp.tell())))

    def __str__(self):
        dumps = []
        dumps.append('----------')
        dumps.append(self.__class__.__name__)
        dumps.append('----------')
        for field in self.fields:
            dumps.append('%s: %s' % (field.name, field.value))
        dumps.append('==========')
        return '\n'.join(dumps)
