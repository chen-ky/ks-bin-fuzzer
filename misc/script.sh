#!/bin/sh

BUILD_DIR='build'

build_lib() {
    ./configure --prefix="$(pwd)/$BUILD_DIR"
    mv ~/scripts/gcc_cov ~/scripts/gcc
    echo Building png library...
    # make check
    make install
    mv ~/scripts/gcc ~/scripts/gcc_cov
}

build_app() {
    mkdir -p "$BUILD_DIR"/app
    cp -P contrib/examples/pngtopng.c "$BUILD_DIR"/app/.
    cd "$BUILD_DIR"/app
    gcc_cov -lgcov --coverage -Wall -L.libs -lpng pngtopng.c -o pngtopng
    cd ../..
}

run() {
    cd "$BUILD_DIR"/app
    LD_PRELOAD=../../.libs/libpng16.so ./pngtopng ../../contrib/testpngs/rgb-alpha-16-1.8.png /dev/null
    cd ../..
}

prepare_cov() {
    cp -P *.c "$BUILD_DIR"/app/
    # cp -P *.h "$BUILD_DIR"/app/
    cp -P .libs/*.gcda "$BUILD_DIR"/app/
    cp -P .libs/*.gcno "$BUILD_DIR"/app/
    cd "$BUILD_DIR"/app
    gcov *.c
    cd ../..
}

clean() {
    make clean
    rm -rf "$BUILD_DIR"
    rm -f *.gcda *.gcno
}

if [ clean = "$1" ]
then
    clean
elif [ build = "$1" ]
then
    build_lib
    build_app
else
    run
    prepare_cov
fi
