meta:
  id: increment_test
  endian: be
seq:
  - id: counter
    type: t_counter
    repeat: expr
    repeat-expr: 5
# instances:
#   ctr_start:
#     value: 0
types:
  t_counter:
    seq:
      - id: counter
        type: u4
        -fz-increment: ctr_start
        # -fz-increment: _parent.ctr_start
        # -fz-increment-step: 1
    instances:
      ctr_start:
        value: 0
        -fz-static: true
