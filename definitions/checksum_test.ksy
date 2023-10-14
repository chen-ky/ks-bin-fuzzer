meta:
  id: checksum_test

seq:
  - id: content
    content: "DEAD BEEF"
  - id: another_content
    content: "CAFE"
  - id: crc32
    size: 4
    -fz-process-crc32: content + another_content
  - id: sha256
    size: 32
    -fz-process-sha256: content + another_content
