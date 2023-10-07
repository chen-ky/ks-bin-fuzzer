meta:
  id: enums_test

seq:
  - id: enum0
    type: u1
    enum: enum_0
  - id: enum1
    type: s1
    enum: enum_1
enums:
  enum_0:
    0: some
    1: stuff
  enum_1:
    0:
      id: what
      doc: What
      doc-ref: https://example.com
    4:
      id: is0
      doc: Is
    6:
      id: this
      doc-ref: https://example.com
    3:
      id: really
