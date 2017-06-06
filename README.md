# expectless
Simple expect library for python


## Usage
we have a script called `test_expect.py` which asks the user for a name and a password to continue. you can easily automate that by creating `expectations dict` like the following

```
    expectations = {
        'name:': 'auser',
        'password:': 'password',
    }
```
and then invoke the script 
```
p = expect(["./test_expect.py"], expectations=expectations)
```

You can also use networked applications as well for instance talking to ssh on a remote machine
```python
p = expect(["ssh", "-T", "ahmed@10.147.19.169"], expectations={"ahmed@10.147.19.169's password:":'***'})
```

## But why?
I wanted to learn about PTYs `Pseudoterminal` and I always liked `expect` tool

## Why two versions (master/pytv)?
    - master uses `subprocess.Popen` which works fine for simple applications. 
    - pytv: uses `pty` implementation


## Next steps:
    - Regular expressions expectations.
    - Interactivity

## Operating systems support?
It's only developed and tested on GNU/Linux operating system, and I've no idea about other operating systems. PRs are welcome.
