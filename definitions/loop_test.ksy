meta:
  id: loop_test
seq:
  - id: length
    type: u1
    -fz-range-min: 1
    -fz-range-max: 2
  - id: until_fruit
    type: u1
    enum: fruits
    repeat: until
    repeat-until: _ == fruits::mango
  - id: expr_fruit
    type: u1
    enum: fruits
    repeat: expr
    repeat-expr: length * 2
  - id: eos_fruit
    type: u1
    enum: fruits
    repeat: eos
    -fz-repeat-min: 1
    -fz-repeat-max: 2
enums:
  fruits:
    0: apple
    1: orange
    2: mango
