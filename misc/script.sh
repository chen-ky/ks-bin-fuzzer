#!/bin/sh

BUILD_DIR='build'
EXCLUDE_FILES="pnglibconf.* pngtest.* example.*"
COVERAGE_REPORT='coverage.csv'
TEST_COUNT=10000
TEST_SECONDS=$(expr '24' '*' '60' '*' '60')

RED='\033[0;31m'
YELLOW_BOLD='\033[1;33m'
CYAN_BOLD='\033[1;36m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

build_lib() {
    ./configure --prefix="$(pwd)"/"$BUILD_DIR"
    mv ~/scripts/gcc_cov ~/scripts/gcc
    echo Building png library...
    # make check
    make install
    mv ~/scripts/gcc ~/scripts/gcc_cov
}

build_app() {
    mkdir -p "$BUILD_DIR"/app
    # cp -P contrib/libtests/readpng.c "$BUILD_DIR"/app/.
    cp -P contrib/examples/pngtopng.c "$BUILD_DIR"/app/.
    cd "$BUILD_DIR"/app
    # gcc_cov -lgcov --coverage -Wall -L.libs -lpng readpng.c -o readpng
    gcc_cov -lgcov --coverage -Wall -L.libs -lpng pngtopng.c -o pngtopng
    cd ../..
}

test() {
    set -e
    cp ../../build/output_fuzzer.py  "$BUILD_DIR"/app/.
    set +e
    cd "$BUILD_DIR"/app
    rm -f test_target_out.txt
    echo 'runs,coverage_percent' > $COVERAGE_REPORT
    SUCCESS=0
    FAILED=0
    RAN=0
    TEST_START_TIME=$(date +%s)
    TEST_END_TIME=$(expr $TEST_SECONDS '+' $TEST_START_TIME)
    # for i in $(seq $TEST_COUNT)
    while [ $(date +%s) -lt $TEST_END_TIME ]
    do
        # echo $i
        python3 output_fuzzer.py > test_file
        # LD_PRELOAD=../../.libs/libpng16.so ./readpng < test_file 2>&1 | tee /dev/tty >> test_target_out.txt
        LD_PRELOAD=../../.libs/libpng16.so ./pngtopng test_file /dev/null 2>&1 | tee /dev/tty >> test_target_out.txt
        if [ $? == 0 ]
        then
            SUCCESS=$(expr $SUCCESS + 1)
        else
            FAILED=$(expr $FAILED + 1)
        fi
        RAN=$(expr $RAN + 1)
        cd ../.. && \
        prepare_cov $RAN $COVERAGE_REPORT && \
        cd "$BUILD_DIR"/app
        rm test_file
    done
    rm output_fuzzer.py
    cd "../.."
    echo -e "${CYAN_BOLD}================================================${NC}"
    echo -e "${CYAN_BOLD}                  Test result                   ${NC}"
    echo -e "${CYAN_BOLD}================================================${NC}"
    echo "🏃 Ran     : $RAN"
    echo "🎉 Passed  : $SUCCESS"
    echo "❌ Failed  : $FAILED"
}

run() {
    cd "$BUILD_DIR"/app
    # LD_PRELOAD=../../.libs/libpng16.so ./readpng < ../../contrib/testpngs/rgb-alpha-16-1.8.png
    LD_PRELOAD=../../.libs/libpng16.so ./pngtopng ../../contrib/testpngs/rgb-alpha-16-1.8.png /dev/null
    cd ../..
}

prepare_cov() {
    cp -P *.c "$BUILD_DIR"/app/
    # cp -P *.h "$BUILD_DIR"/app/
    cp -P .libs/*.gcda "$BUILD_DIR"/app/
    cp -P .libs/*.gcno "$BUILD_DIR"/app/
    cd "$BUILD_DIR"/app
    rm -r $EXCLUDE_FILES
    gcov *.c | tee gcov_out.txt | tail -n1 | tee /dev/tty | sed -e "s/^Lines executed:/$1,/" | sed -e 's/% of [0-9]*$//' >> $2
    cd ../..
}

clean_cov() {
    rm -f *.gcda *.gcov
    cd .libs
    rm -f *.gcda *.gcov
    cd ..
    cd "$BUILD_DIR"
    rm -f *.gcda *.gcov
    rm -f gcov_out.txt
    rm -f $COVERAGE_REPORT
    cd ..
}

clean() {
    make clean
    rm -rf "$BUILD_DIR"
    rm -f *.gcda *.gcno
}

cd libpng-1.6.40

if [ clean = "$1" ]
then
    clean
elif [ build = "$1" ]
then
    build_lib
    build_app
elif [ test = "$1" ]
then
    clean_cov
    test
else
    run
    prepare_cov
fi
