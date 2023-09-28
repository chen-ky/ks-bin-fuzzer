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

    def append(self, buffer: bytes | bytearray):
        # FIXME does not take into account ptr
        self.data += buffer
        self.end_pos += len(buffer)

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
