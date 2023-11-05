meta:
  id: switch_on_test
seq:
  - id: type
    type: u1
    enum: types
  - id: length
    type: u1
    -fz-attr-len: value
  - id: value
    type:
      switch-on: type
      cases:
        types::empty_body: empty_body
        types::body_0: body_0
        types::body_1: body_1
types:
  empty_body:
    seq:
      - id: data
        size: 0
  body_0:
    seq:
      - id: data
        size-eos: true
        -fz-size-min: 1
        -fz-size-max: 128
  body_1:
    seq:
      - id: data
        type: u4be
enums:
  types:
    0: empty_body
    1: body_0
    2: body_1
