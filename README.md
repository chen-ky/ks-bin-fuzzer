<img style="display: block;" src='misc/logo.png' width=64px>

# ks-bin-fuzzer

Kaitai Struct compiler to produce format specific binary fuzzer

Requires Python 3.11 and above.

## Running the compiler

1. Run the `run.sh` script provided in the root directory of this repository and provide the Kaitai Struct file to the script. For example: `./run.sh definitions/animal.ksy`

2. The generated fuzzer is located in the `build` directory.

## Kaitai Struct DSL extensions

| Key                       | Description                                                                                                                                                                                                            |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-fz-attr-len`            | Mark this field as a length field of another field. The value of this field will be automatically populated by the byte length of said field.                                                                          |
| `-fz-choice`              | Randomly pick an option from the list of choices available.                                                                                                                                                            |
| `-fz-order`               | Produce an output in a specific order, as defined in the list provided. The value will be removed from the list once it is picked. Only useful in a loop.                                                              |
| `-fz-random-order`        | Similar to `-fz-order`, except it picks value from the list randomly on run-time.                                                                                                                                      |
| `-fz-process-<algorithm>` | Populate the field with the result of the algorithm (produces byte type), applied to the specified field. See [here](#algorithms-available) for the list of supported algorithm.                                       |
| `-fz-range-min`           | Minimum value (inclusive) that can be generated. Only works for numbers. Optional. Defaults to the minimum value of the number type.                                                                                   |
| `-fz-range-max`           | Maximum value (inclusive) that can be generated. Only works for numbers. Optional. Defaults to the maximum value of the number type.                                                                                   |
| `-fz-repeat-min`          | Repeat for a minimum (inclusive) number of times. Only valid for `repeat: eos`.                                                                                                                                        |
| `-fz-repeat-max`          | Repeat for a maximum (inclusive) number of times. Only valid for `repeat: eos`.                                                                                                                                        |
| `-fz-size-min`            | Minimum size (inclusive) of the field that can be generated. Used when the size of the field cannot be determined by its `type`. Optional. Defaults to 0.                                                              |
| `-fz-size-max`            | Maximum size (inclusive) of the field that can be generated. Required when the size of the field cannot be determined by its `type`.                                                                                   |
| `-fz-static`              | Mark a variable as a static variable. Only works in the `instances` block.                                                                                                                                             |
| `-fz-increment`           | Contains a reference to another variable. A field with this key will be populated by the value stored in the referenced variable. The variable is incremented after populating the field. Only works for integer type. |
| `-fz-increment-step`      | Specify the number used to increment the variable in `-fz-increment`. Optional. Defaults to 1.                                                                                                                  |

### Algorithms Available

`crc32`,
`md5`,
`sha1`,
`sha224`,
`sha256`,
`sha384`,
`sha512`,
`sha3-224`,
`sha3-256`,
`sha3-384`,
`sha3-512`

## Running tests

From the root directory of this repository, run:

```
pytest tests
```

### Code coverage

```sh
coverage run --branch --source=src -m pytest tests && coverage html
```
