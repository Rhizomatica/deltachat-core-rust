# Delta Chat RPC python client

RPC client connects to standalone Delta Chat RPC server `deltachat-rpc-server`
and provides asynchronous interface to it.

## Getting started

To use Delta Chat RPC client, first build a `deltachat-rpc-server` with `cargo build -p deltachat-rpc-server`
or download a prebuilt release.
Install it anywhere in your `PATH`.

[Create a virtual environment](https://docs.python.org/3/library/venv.html)
if you don't have one already and activate it.
```
$ python -m venv env
$ . env/bin/activate
```

Install `deltachat-rpc-client` from source:
```
$ cd deltachat-rpc-client
$ pip install .
```

## Testing

1. Build `deltachat-rpc-server` with `cargo build -p deltachat-rpc-server`.
2. Run `PATH="../target/debug:$PATH" tox`.

Additional arguments to `tox` are passed to pytest, e.g. `tox -- -s` does not capture test output.

## Using in REPL

Setup a development environment:
```
$ tox --devenv env
$ . env/bin/activate
```

It is recommended to use IPython, because it supports using `await` directly
from the REPL.

```
$ pip install ipython
$ PATH="../target/debug:$PATH" ipython
...
In [1]: from deltachat_rpc_client import *
In [2]: rpc = Rpc()
In [3]: await rpc.start()
In [4]: dc = DeltaChat(rpc)
In [5]: system_info = await dc.get_system_info()
In [6]: system_info["level"]
Out[6]: 'awesome'
In [7]: await rpc.close()
```
