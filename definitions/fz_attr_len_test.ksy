meta:
  id: fz_attr_len_test
  endian: le

seq:
  - id: len
    type: u4
    -fz-attr-len: body_len + body + trailer  # Expected value: 13
  - id: body_len
    type: u4
    -fz-attr-len: body  # Expected value: 6
  - id: body
    contents: random
  - id: trailer
    contents: ["END"]