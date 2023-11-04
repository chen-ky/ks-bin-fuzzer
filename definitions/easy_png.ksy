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
    type: u4
    valid: 13
  - id: ihdr_type
    contents: "IHDR"
  - id: ihdr
    type: ihdr_chunk
  - id: ihdr_crc
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
        # -fz-order: ["IDAT", "IEND"]
        -fz-order: ["bKGD", "PLTE", "sRGB", "cHRM", "gAMA", "pHYs", "tIME", "iTXt", "tEXt", "IDAT", "zTXt", "IEND"]
      - id: body
        size: len
        type:
          switch-on: type
          cases:
            # Critical chunks
            '"IHDR"': ihdr_chunk
            '"PLTE"': plte_chunk
            '"IDAT"': idat_chunk
            '"IEND"': iend_chunk

#             # Ancillary chunks
            '"cHRM"': chrm_chunk
            '"gAMA"': gama_chunk
#             # # iCCP
#             # # sBIT
            '"sRGB"': srgb_chunk
            '"bKGD"': bkgd_chunk
#             # # hIST
#             # # tRNS
            '"pHYs"': phys_chunk
#             # # sPLT
            '"tIME"': time_chunk
            '"iTXt"': international_text_chunk
            '"tEXt"': text_chunk
            '"zTXt"': compressed_text_chunk

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
        # -fz-choice: [1, 2, 4, 8, 16]  # For greyscale, does not support bit generation yet, so minimum is 8
        # -fz-choice: [8, 16]  # For truecolor and truecolor_alpha, greyscale_alpha
        -fz-choice: [8]  # For indexed
      - id: color_type
        type: u1
        enum: color_type
        # -fz-choice: [color_type::truecolor_alpha, color_type::truecolor, color_type::greyscale_alpha, color_type::greyscale]
        # -fz-choice: [color_type::truecolor_alpha, color_type::truecolor]
        # -fz-choice: [color_type::greyscale_alpha, color_type::greyscale]
        # -fz-choice: [color_type::indexed]
      - id: compression_method
        type: u1
        valid: 0
        # -fz-choice: [0]
      - id: filter_method
        type: u1
        valid: 0
        # -fz-choice: [0]
      - id: interlace_method
        type: u1
        -fz-choice: [0]  # https://www.w3.org/TR/png/#8InterlaceMethods
  plte_chunk:
    doc-ref: https://www.w3.org/TR/png/#11PLTE
    seq:
      - id: entries
        type: rgb
        repeat: eos
        -fz-repeat-min: 1
        -fz-repeat-max: 256
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
                color_type::indexed: indexed_scanline
                color_type::greyscale: greyscale_scanline
                color_type::greyscale_alpha: greyscale_alpha_scanline
            repeat: expr
            repeat-expr: _root.ihdr.height
        types:
          indexed_scanline:
            seq:
            - id: filter
              type: u1
              enum: scanline_filter
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8)
          truecolor_scanline:
            seq:
            - id: filter
              type: u1
              enum: scanline_filter
              # valid: scanline_filter::none
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8) * 3
          truecolor_alpha_scanline:
            seq:
            - id: filter
              type: u1
              enum: scanline_filter
              # valid: scanline_filter::none
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8) * 4
          greyscale_scanline:
            seq:
            - id: filter
              type: u1
              enum: scanline_filter
              # valid: scanline_filter::none
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8) * 1
          greyscale_alpha_scanline:
            seq:
            - id: filter
              type: u1
              enum: scanline_filter
              # valid: scanline_filter::none
            - id: data
              size: _root.ihdr.width * (_root.ihdr.bit_depth / 8) * 2
        enums:
          scanline_filter:
            0: none
            1: sub
            2: up
            3: average
            4: paeth
  chrm_chunk:
    doc-ref: https://www.w3.org/TR/png/#11cHRM
    seq:
      - id: white_point
        type: point
      - id: red
        type: point
      - id: green
        type: point
      - id: blue
        type: point
  point:
    seq:
      - id: x_int
        type: u4
      - id: y_int
        type: u4
    instances:
      x:
        value: x_int / 100000.0
      y:
        value: y_int / 100000.0
  gama_chunk:
    doc-ref: https://www.w3.org/TR/png/#11gAMA
    seq:
      - id: gamma_int
        type: u4
    instances:
      gamma_ratio:
        value: 100000.0 / gamma_int
  iend_chunk:
    seq:
      - id: empty_body
        size: 0
  text_chunk:
    doc: |
      Text chunk effectively allows to store key-value string pairs in
      PNG container. Both "key" (keyword) and "value" (text) parts are
      given in pre-defined subset of iso8859-1 without control
      characters.
    doc-ref: https://www.w3.org/TR/png/#11tEXt
    seq:
      - id: keyword
        type: strz
        encoding: iso8859-1
        doc: Indicates purpose of the following text data.
        -fz-size-min: 1
        -fz-size-max: 80
      - id: text
        type: str
        size-eos: true
        encoding: iso8859-1
        -fz-size-min: 0
        -fz-size-max: 2048
  compressed_text_chunk:
    doc: |
      Compressed text chunk effectively allows to store key-value
      string pairs in PNG container, compressing "value" part (which
      can be quite lengthy) with zlib compression.
    doc-ref: https://www.w3.org/TR/png/#11zTXt
    seq:
      - id: keyword
        type: strz
        encoding: UTF-8
        doc: Indicates purpose of the following text data.
        -fz-size-min: 1
        -fz-size-max: 80
      - id: compression_method
        type: u1
        enum: compression_methods
      - id: text_datastream
        process: zlib
        -fz-size-min: 0
        -fz-size-max: 2048
        size-eos: true
  srgb_chunk:
    doc-ref: https://www.w3.org/TR/png/#11sRGB
    seq:
      - id: render_intent
        type: u1
        enum: intent
    enums:
      intent:
        0: perceptual
        1: relative_colorimetric
        2: saturation
        3: absolute_colorimetric
  bkgd_chunk:
    doc: |
      Background chunk stores default background color to display this
      image against. Contents depend on `color_type` of the image.
    doc-ref: https://www.w3.org/TR/png/#11bKGD
    seq:
      - id: bkgd
        type:
          switch-on: _root.ihdr.color_type
          cases:
            color_type::greyscale: bkgd_greyscale
            color_type::greyscale_alpha: bkgd_greyscale
            color_type::truecolor: bkgd_truecolor
            color_type::truecolor_alpha: bkgd_truecolor
            color_type::indexed: bkgd_indexed
  bkgd_greyscale:
    doc: Background chunk for greyscale images.
    seq:
      - id: value
        type: u2
  bkgd_truecolor:
    doc: Background chunk for truecolor images.
    seq:
      - id: red
        type: u2
      - id: green
        type: u2
      - id: blue
        type: u2
  bkgd_indexed:
    doc: Background chunk for images with indexed palette.
    seq:
      - id: palette_index
        type: u1
  phys_chunk:
    doc: |
      "Physical size" chunk stores data that allows to translate
      logical pixels into physical units (meters, etc) and vice-versa.
    doc-ref: https://www.w3.org/TR/png/#11pHYs
    seq:
      - id: pixels_per_unit_x
        type: u4
        doc: |
          Number of pixels per physical unit (typically, 1 meter) by X
          axis.
      - id: pixels_per_unit_y
        type: u4
        doc: |
          Number of pixels per physical unit (typically, 1 meter) by Y
          axis.
      - id: unit
        type: u1
        enum: phys_unit
  time_chunk:
    doc: |
      Time chunk stores time stamp of last modification of this image,
      up to 1 second precision in UTC timezone.
    doc-ref: https://www.w3.org/TR/png/#11tIME
    seq:
      - id: year
        type: u2
      - id: month
        type: u1
      - id: day
        type: u1
      - id: hour
        type: u1
      - id: minute
        type: u1
      - id: second
        type: u1
  international_text_chunk:
    doc: |
      International text chunk effectively allows to store key-value string pairs in
      PNG container. Both "key" (keyword) and "value" (text) parts are
      given in pre-defined subset of iso8859-1 without control
      characters.
    doc-ref: https://www.w3.org/TR/png/#11iTXt
    seq:
      - id: keyword
        type: strz
        encoding: UTF-8
        -fz-size-min: 1
        -fz-size-max: 80
        doc: Indicates purpose of the following text data.
      - id: compression_flag
        type: u1
        doc: |
          0 = text is uncompressed, 1 = text is compressed with a
          method specified in `compression_method`.
        -fz-choice: [0, 1]
      - id: compression_method
        type: u1
        enum: compression_methods
      - id: language_tag
        type: strz
        encoding: ASCII
        doc: |
          Human language used in `translated_keyword` and `text`
          attributes - should be a language code conforming to ISO
          646.IRV:1991.
        -fz-size-min: 1
        -fz-size-max: 127
      - id: translated_keyword
        type: strz
        encoding: UTF-8
        doc: |
          Keyword translated into language specified in
          `language_tag`. Line breaks are not allowed.
        -fz-size-min: 1
        -fz-size-max: 80
      - id: uncompressed_text
        if: compression_flag == 0
        type: str
        encoding: UTF-8
        -fz-size-min: 0
        -fz-size-max: 2048
        size-eos: true
        doc: |
          Text contents ("value" of this key-value pair), written in
          language specified in `language_tag`. Line breaks are
          allowed.
      - id: zlib_compressed_text
        if: compression_flag == 1 and compression_method == compression_methods::zlib
        # type: str
        # encoding: UTF-8
        process: zlib
        -fz-size-min: 0
        -fz-size-max: 2048
        size-eos: true
        doc: |
          Text contents ("value" of this key-value pair), written in
          language specified in `language_tag`. Line breaks are
          allowed.
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
  phys_unit:
    0: unknown
    1: meter
  compression_methods:
    0: zlib
