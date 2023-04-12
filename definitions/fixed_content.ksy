# https://doc.kaitai.io/user_guide.html#magic

meta:
  id: fixed_length

seq:
  - id: magic1
    contents: JFIF
    # expects bytes: 4A 46 49 46
  - id: magic2
    # we can use YAML block-style arrays as well
    contents:
      - 0xca
      - 0xfe
      - 0xba
      - 0xbe
    # expects bytes: CA FE BA BE
  - id: magic3
    contents: [CAFE, 0, BABE]
    # expects bytes: 43 41 46 45 00 42 41 42 45
  - id: magic4
    contents: [foo, 0, A, 0xa, 42]
    # expects bytes: 66 6F 6F 00 41 0A 2A
  - id: magic5
    contents: [1, 0x55, "▒,3", 3]
    # expects bytes: 01 55 E2 96 92 2C 33 03
