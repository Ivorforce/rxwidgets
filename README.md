# General

This package adds functionality useful for making [ReactiveX](https://rxpy.readthedocs.io) powered [ipywidgets](https://ipywidgets.readthedocs.io/en/latest/).

Note that this package is in its Beta stage and may change interfaces slightly before a 1.0 release.

# Installation

Run `poetry add rxwidgets`

# Usage

```py
import rxwidgets.ipython as rxi

@rxi.interact_manual
def b(a=(1,5)):
    return a * 5

@rxi.interact
def c(b=b, c=(10, 20)):
    c = b + c
    print(f"C: {c}")
```

Corresponds roughly to native ipywidgets:

```py
from ipywidgets import interact, interact_manual

@interact_manual
def b(a=(1,5)):
    b = a * 5

    @interact
    def c(c=(10, 20)):
        c = b + c
        print(f"C: {c}")
```

An incomprehensive feature list is provided in the `examples` folder.

# Streams

A function stream consists of these steps:

1. `@rxi.stream_defaults`
   - Convert parameter defaults into observables - may display ipywidgets.
   - Convert function into a stream of its results from input streams.
   - In stream: Curry the function and make wrap into a `ValueBox`.
   - Object in stream: `ValueBox(partial(fn, ...))`
2. `@rxi.defer`, `@rxi.pre_load`, ...
   - If desired, apply operators to the call-ready function
3. `@rxi.apply`
    - Create and display an `rxi.Screen`.
    - In stream: Run the function inside the screen and return results as a `ValueBox`.
    - Object in stream: `ValueBox(fn(...))`
4. `@rxi.Automap`
    - If desired, pack the final stream into an `Automap` object. This object maps all operators to operators applied inside the stream.
