# https://doc.kaitai.io/user_guide.html#magic

meta:
  id: len_after_process
  endian: be

seq:
  - id: len
    type: u4
    -fz-attr-len: body
  - id: body
    size-eos: true
    process: zlib
