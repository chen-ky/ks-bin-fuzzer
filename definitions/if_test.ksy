meta:
  id: if_test
seq:
  - id: type
    type: u1
    enum: types
  - id: length
    type: u1
    -fz-attr-len: value_0 + value_1
  - id: value_0
    size-eos: true
    -fz-size-min: 1
    -fz-size-max: 128
    if: type == types::body_0
  - id: value_1
    type: u4be
    if: type == types::body_1
enums:
  types:
    0: empty_body
    1: body_0
    2: body_1
