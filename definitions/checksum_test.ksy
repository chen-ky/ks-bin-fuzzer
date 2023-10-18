meta:
  id: checksum_test

seq:
  - id: content
    contents: "DEAD BEEF"
  - id: another_content
    contents: "CAFE"
  - id: crc32
    size: 4
    -fz-process-crc32: content + another_content
  - id: sha256
    size: 32
    -fz-process-sha256: content + another_content
