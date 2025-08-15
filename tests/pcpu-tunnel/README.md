# pcpu throughput test

1. `scp` the entire `tests/` directory to `east`, `west`, `sunset`, and
   `sunrise`.
1. On `east`, run: `./tests/pcpu-tunnel/01-east-init.sh` and
   follow the on screen instructions. There will be some extra debug output --
   ignore that.
1. On `west`, run `./tests/pcpu-tunnel/02-west-init.sh`. Same
   notes as for `east`.
1. On `sunset`, run: `RUNS=1 ./tests/pcpu-tunnel/sunset-neper.sh 32`, or vary
   the parameters as desired
1. Finally on `sunrise`, run: `RUNS=1 DURATION=10 ./tests/pcpu-tunnel/sunrise-neper.sh 32`,
   or vary the parameters as desired
