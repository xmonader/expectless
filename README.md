# expectless
Simple expect library for python


## Usage
we have a script called `test_expect.py` which asks the user for a name and a password to continue. you can easily automate that by creating `expectations list` like the following

```
    expectations = [
        ('name:', 'ahmed'),
        ('password:', 'ahardpassword'),
    ]
```
and then invoke the script 
```
p = expect(["./test_expect.py"], expectations=expectations)
```

You can also use networked applications as well for instance talking to ssh on a remote machine
```python
    p = expect(["ssh", "-T", "mie@10.147.19.169", "ls /home"], expectations=[("mie@10.147.19.169's password:", 'apa')])
```

## Interactivity
You can interact with the application 
```
    p = expect(["python3"])    
    interact(p[0])
```

## But why?
I wanted to learn about PTYs `Pseudoterminal` and I always liked `expect` tool


## Next steps:
    - Regular expressions expectations.

## Operating systems support?
It's only developed and tested on GNU/Linux operating system, and I've no idea about other operating systems. PRs are welcome.
