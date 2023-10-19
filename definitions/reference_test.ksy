meta:
  id: reference_test
  endian: le

seq:
  - id: len
    type: u4
    -fz-attr-len: body + trailer
  - id: body
    contents: asdiodkdkalaasndfjksdnf
  - id: trailer
    contents: ["END"]