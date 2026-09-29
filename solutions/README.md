# Reference Solutions — spoilers!

There is one folder per problem, mirroring the problem folders. Each file is a drop-in
replacement for the starter module, and comments mark the key ideas and gotchas.

Try each problem yourself first. When you compare, focus on **what you missed**
(edge cases, stdlib tools, idioms) rather than on matching the code line for line.
There are many valid solutions.

To run the tests against these solutions instead of your code (from the project root):

```bash
pipenv run pytest --solutions                    # all problems
pipenv run pytest 08_transactional_kv_store --solutions
```
