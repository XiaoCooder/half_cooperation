# TASK-002 Round 001 Test Report

## Commands Run

```bash
python3 -m unittest discover -s /home/usr/blog-test/tests
```

## Result

Passed.

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
```

## Coverage

- Verifies the homepage includes the required profile, recent updates, featured projects, social links, and footer content.
- Verifies the page contains 4 recent updates and 2 featured project cards, which stays within the requested ranges.
- Verifies the avatar asset, GitHub/Zhihu/email links, and dynamic footer year hook exist.
- Verifies mobile media queries and hover/upward-motion affordances are defined in CSS.
