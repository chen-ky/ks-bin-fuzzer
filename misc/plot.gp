# Output Settings
set terminal pngcairo size 1080,810
set output 'cov.png'
# Labels, Title and Data
set datafile separator comma
set key outside bottom right
set xlabel 'Runs'
set ylabel 'Coverage Percentage'
set title 'Coverage Graph'

plot \
"../results/unmodded_fuzz_png/coverage.csv" using 1:2 lc rgb 'dark-spring-green' lw 1.5 title 'fuzz\_png.ksy' with lines, \
"../results/unmodded_easy_png/coverage.csv" using 1:2 lc rgb 'blue' lw 1.5 title 'easy\_png.ksy' with lines, \
# "results/benchmark_coarse.txt" using 1:3 lc rgb 'dark-spring-green' notitle with points, \
# "results/benchmark_coarse_rwlock.txt" using 1:3 lc rgb 'blue' notitle with points, \
# "results/benchmark_fine_mutex_avg.txt" using 1:3 lc rgb 'gold' title 'Fine lock with mutex' with lines, \
# "results/benchmark_fine_mutex.txt" using 1:3 lc rgb 'gold' notitle with points, \
# "results/benchmark_avg.txt" using 1:3 lc rgb 'dark-magenta' title 'Fine lock with rwlock' with lines, \
# "results/benchmark.txt" using 1:3 lc rgb 'dark-magenta' notitle with points