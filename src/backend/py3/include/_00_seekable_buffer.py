from __future__ import annotations
from typing import Optional


class SeekableBuffer():

    def __init__(self, data: Optional[bytearray] = None, start_pos: Optional[int] = None, end_pos: Optional[int] = None) -> None:
        data = bytearray() if data is None else data
        if start_pos is not None and start_pos >= len(data):
            raise ValueError(
                "Start position cannot be greater than or equal to the length of the underlying data")
        if start_pos is None or start_pos < 0:
            start_pos = 0
        if end_pos is not None and end_pos < start_pos:
            raise ValueError(
                "End position cannot be less than the start position")
        if end_pos is None or end_pos > len(data):
            end_pos = len(data)
        self.data = data
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.ptr = self.start_pos

    def _grow_buf(self, n_bytes: int) -> None:
        if self.is_subbuffer():
            raise BufferError("Sub-buffer cannot be grown")
        self.data.extend(b"\0" * n_bytes)
        self.end_pos += n_bytes

    def _move_data(self, offset: int, write_null_bytes: bool = True) -> None:
        """Move data on and after the pointer by an offset, will not change the pointer position.

        :param offset: To move to the right, specify a positive offset. To move to the left, specify a negative offset.
        :param write_null_bytes: Write null bytes to region that is originally occupied by the data

        :raises ValueError: Invalid offset
        """
        if offset == 0:
            return
        elif self.ptr + offset < self.start_pos:
            raise ValueError("Cannot move data beyond the start of the buffer")
        data_to_move = self.data[self.ptr:]
        for i, b in enumerate(data_to_move):
            if self.ptr + offset + i >= self.end_pos:
                break
            self.data[self.ptr + offset + i] = b
        if write_null_bytes:
            if offset > 0:
                for i in range(self.ptr, self.ptr + offset):
                    self.data[i] = 0
            else:
                for i in range(self.end_pos + offset, self.end_pos):
                    self.data[i] = 0

    def append(self, buffer: bytes | bytearray):
        # FIXME does not take into account ptr
        self.data += buffer
        self.end_pos += len(buffer)

    def write(self, buffer: bytes | bytearray):
        # TODO
        for b in buffer:
            pass

    def get_data(self, n_bytes: Optional[int] = None):
        """Get data using the pointer"""
        if n_bytes is not None:
            end = self.ptr + n_bytes
        else:
            end = self.end_pos
        if end > self.end_pos:
            end = self.end_pos
        result = bytes(self.data[self.ptr:end])
        self.ptr = end
        return result

    def get_full_data(self) -> bytes:
        """Get a copy of the data in the buffer"""
        return bytes(self.data[self.start_pos:self.end_pos])

    def is_eos(self) -> bool:
        return self.ptr == self.end_pos

    def is_subbuffer(self) -> bool:
        # Not sub buffer if length is equal to underlying data length
        return len(self) != len(self.data)

    def seek(self, offset: int) -> None:
        """Set pointer be at an offset relative to the start of the buffer"""
        if offset < 0:
            raise ValueError("Offset cannot be negative")
        new_ptr = offset + self.start_pos
        if new_ptr > self.end_pos:
            new_ptr = self.end_pos
        self.ptr = new_ptr

    def __len__(self) -> int:
        return self.end_pos - self.start_pos
