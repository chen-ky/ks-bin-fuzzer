meta:
  id: example
  endian: be
seq:
  - id: desc
    type: u1
    enum: desc_type
  - id: data
    type: custom_type
types:
  custom_type:
    seq:
      - id: sku
        type: u4
      - id: val
        type: s4
    instances:
      val_times_ten:
        value: val * 10
enums:
  desc_type:
    0: quantity
    1: price