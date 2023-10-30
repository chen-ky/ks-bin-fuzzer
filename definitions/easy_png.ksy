meta:
  id: png
  title: PNG (Portable Network Graphics) file
  file-extension:
    - png
    - apng
  xref:
    forensicswiki: Portable_Network_Graphics_(PNG)
    iso: 15948:2004
    justsolve:
      - PNG
      - APNG
    loc: fdd000153
    mime:
      - image/png
      - image/apng
      - image/vnd.mozilla.apng
    pronom:
      - fmt/11 # PNG 1.0
      - fmt/12 # PNG 1.1
      - fmt/13 # PNG 1.2
      - fmt/935 # APNG
    rfc: 2083
    wikidata:
      - Q178051 # PNG
      - Q433224 # APNG
  license: CC0-1.0
  ks-version: 0.9
  endian: be
doc: |
  Test files for APNG can be found at the following locations:

    * <https://philip.html5.org/tests/apng/tests.html>
    * <http://littlesvr.ca/apng/>
seq:
  # https://www.w3.org/TR/png/#5PNG-file-signature
  - id: magic
    contents: [137, 80, 78, 71, 13, 10, 26, 10]
  # https://www.w3.org/TR/png/#11IHDR
  # Always appears first, stores values referenced by other chunks
  - id: ihdr_len
    # Pay attention to this, int.to_bytes(13, length=4, byteorder="big", signed=False)
    type: u4
    valid: 13
  - id: ihdr_type
    contents: "IHDR"
  - id: ihdr
    type: ihdr_chunk
  - id: ihdr_crc
    # int.to_bytes(zlib.crc32(ihdr_type + ihdr), length=4, byteorder="big", signed=False)
    size: 4
    -fz-process-crc32: ihdr_type + ihdr
  # The rest of the chunks
  - id: chunks
    type: chunk
    repeat: until
    # https://doc.kaitai.io/user_guide.html#_repeat_until_condition_is_met
    # Underscore (_) is used as a special variable name that refers to the element that we’ve just parsed. When parsing an array of user types, it is possible to write a repeat-until expression that would reference some attribute inside that user type:
    repeat-until: _.type == "IEND" or _io.eof
types:
  chunk:
    seq:
      - id: len  # Size after processing
        type: u4
        -fz-attr-len: body
      - id: type
        type: str
        size: 4
        encoding: UTF-8
        -fz-order: ["IDAT", "IEND"]
        # -fz-order: ["IHDR", "IEND"]
      - id: body
        size: len
        type:
          switch-on: type
          cases:
            # Critical chunks
            '"IHDR"': ihdr_chunk
            # '"PLTE"': plte_chunk
            '"IDAT"': idat_chunk
            '"IEND"': iend_chunk

#             # Ancillary chunks
#             # '"cHRM"': chrm_chunk
#             # '"gAMA"': gama_chunk
#             # # iCCP
#             # # sBIT
#             # '"sRGB"': srgb_chunk
#             # '"bKGD"': bkgd_chunk
#             # # hIST
#             # # tRNS
#             # '"pHYs"': phys_chunk
#             # # sPLT
#             # '"tIME"': time_chunk
#             # '"iTXt"': international_text_chunk
#             # '"tEXt"': text_chunk
#             # '"zTXt"': compressed_text_chunk

#             # # animated PNG chunks
#             # '"acTL"': animation_control_chunk
#             # '"fcTL"': frame_control_chunk
#             # '"fdAT"': frame_data_chunk
      - id: crc
        size: 4
        -fz-process-crc32: type + body
  ihdr_chunk:
    doc-ref: https://www.w3.org/TR/png/#11IHDR
    seq:
      - id: width
        type: u4
        -fz-range-min: 1
        -fz-range-max: 1024
      - id: height
        type: u4
        -fz-range-min: 1
        -fz-range-max: 1024
      - id: bit_depth
        type: u1
        # -fz-choice: [1, 2, 4, 8]  # For greyscale and greyscale_alpha, does not support bit generation yet, so minimum is 8
        # -fz-choice: [8]  # For greyscale and greyscale_alpha
        -fz-choice: [8, 16]  # For truecolor and truecolor_alpha
      - id: color_type
        type: u1
        enum: color_type
        # -fz-choice: [color_type::truecolor_alpha, color_type::truecolor, color_type::greyscale_alpha, color_type::greyscale]
        -fz-choice: [color_type::truecolor_alpha, color_type::truecolor]
        # -fz-choice: [color_type::greyscale_alpha, color_type::greyscale]
      - id: compression_method
        type: u1
        -fz-choice: [0]
      - id: filter_method
        type: u1
        -fz-choice: [0]
      - id: interlace_method
        type: u1
        -fz-choice: [0]
#     instances:
#       channel:
#         value: "color_type == color_type::truecolor_alpha ? 4 : color_type == color_type::greyscale ? 2 : 0"
  plte_chunk:
    doc-ref: https://www.w3.org/TR/png/#11PLTE
    seq:
      - id: entries
        type: rgb
        # repeat: eos
  idat_chunk:
    seq:
      - id: data
        size: _parent.len # This is the size after processing
        type: scanlines
        process: zlib
    types:
      scanlines:
        seq:
          - id: scanline
            type:
              switch-on: _root.ihdr.color_type
              cases:
                color_type::truecolor: truecolor_scanline
                color_type::truecolor_alpha: truecolor_alpha_scanline
                color_type::greyscale: greyscale_scanline
                color_type::greyscale_alpha: greyscale_alpha_scanline
            repeat: expr
            repeat-expr: _root.ihdr.height
        types:
          truecolor_scanline:
            seq:
            - id: filter
              type: u1
              -fz-choice: [0]
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8) * 3
          truecolor_alpha_scanline:
            seq:
            - id: filter
              type: u1
              -fz-choice: [0]
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8) * 4
          greyscale_scanline:
            seq:
            - id: filter
              type: u1
              -fz-choice: [0]
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8) * 1
          greyscale_alpha_scanline:
            seq:
            - id: filter
              type: u1
              -fz-choice: [0]
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8) * 2
  iend_chunk:
    seq:
      - id: empty_body
        size: 0
  rgb:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1
  rgba:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1
      - id: a
        type: u1 

enums:
  color_type:
    0: greyscale
    2: truecolor
    3: indexed
    4: greyscale_alpha
    6: truecolor_alpha
