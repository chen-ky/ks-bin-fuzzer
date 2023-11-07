meta:
  id: increment_test
  endian: be
# Method 1
seq:
  - id: counter
    type: t_counter
    repeat: expr
    repeat-expr: 5
types:
  t_counter:
    seq:
      - id: counter
        type: u4
        -fz-increment: ctr_start
    instances:
      ctr_start:
        value: 0
        -fz-static: true

# Method 2
# seq:
#   - id: counter
#     type: t_counter
#     repeat: expr
#     repeat-expr: 5
# instances:
#   ctr_start:
#     value: 0
# types:
#   t_counter:
#     seq:
#       - id: counter
#         type: u4
#         -fz-increment: _parent.ctr_start
#         -fz-increment-step: 1

# Method 3
# seq:
#   - id: counter
#     type: u4
#     -fz-increment: ctr_start
#     -fz-increment-step: 1
#     repeat: expr
#     repeat-expr: 5

# instances:
#   ctr_start:
#     value: 0
#     -fz-static: true
