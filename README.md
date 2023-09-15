# ks-bin-fuzzer
Binary Fuzzer utilising Kaitai Struct

## Running tests

From the root directory of this repository, run:

```
pytest tests
```

## Compiling ksc

```
sdk instal sbt
```

```
sbt --error compilerJVM/stage
```

```
 pip install --pre git+https://github.com/kaitai-io/kaitai_struct_python_runtime.git@serialization
```
