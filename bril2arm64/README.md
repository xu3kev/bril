### Usage

```bash
bril2json < test.bril | python3 bril2arm64.py > test.s
gcc-8 -o test test.s
```
