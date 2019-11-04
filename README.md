Command line tool to measure the short term memory on linux system.
### Typical usage:

```bash
$ seq 0 9 | span show; span check
![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `New test`
808
Right: 3
$ seq 0 9 | span show; span check
8012
Right: 4
$ seq 0 9 | span show; span check
47570
Wrong: 5
$ seq 0 9 | span show; span check
9034
Wrong: 4

```

It stores the history of your inputs in ~/.local/share/span/history.tsv.
