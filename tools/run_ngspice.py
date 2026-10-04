#!/usr/bin/env python3
"""Run a smoke-test deck with ngspice, including KiCad's Windows shared library."""

import argparse
import ctypes
import os
from pathlib import Path
import shutil
import subprocess


def run(deck, dll=None):
    executable = shutil.which('ngspice')
    if executable and not dll:
        result = subprocess.run([executable, '-b', str(deck)], capture_output=True, text=True)
        return result.returncode, result.stdout + result.stderr
    dll = dll or os.environ.get('NGSPICE_DLL')
    if not dll:
        raise RuntimeError('Install ngspice or set NGSPICE_DLL to KiCad/bin/ngspice.dll')
    handle = os.add_dll_directory(str(Path(dll).resolve().parent)) if os.name == 'nt' else None
    lib = ctypes.CDLL(str(dll))
    lines, exits = [], []
    send = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
    exit_cb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
    output = send(lambda s, ident, user: (lines.append(s.decode('utf-8', errors='replace')), 0)[1])
    status = send(lambda s, ident, user: 0)
    on_exit = exit_cb(lambda code, immediate, requested, ident, user: (exits.append(code), 0)[1])
    lib.ngSpice_Init.argtypes = [send, send, exit_cb, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    lib.ngSpice_Init.restype = ctypes.c_int
    lib.ngSpice_Command.argtypes = [ctypes.c_char_p]
    lib.ngSpice_Command.restype = ctypes.c_int
    if lib.ngSpice_Init(output, status, on_exit, None, None, None, None):
        raise RuntimeError('ngSpice_Init failed')
    # The shared API accepts UTF-8 circuit lines directly, avoiding source's
    # platform-dependent filename quoting. Control sections run synchronously.
    lines_in = Path(deck).read_text(encoding='utf-8').splitlines()
    circuit = (ctypes.c_char_p * (len(lines_in)+1))(
        *(line.encode('utf-8') for line in lines_in), None)
    lib.ngSpice_Circ.argtypes = [ctypes.POINTER(ctypes.c_char_p)]
    lib.ngSpice_Circ.restype = ctypes.c_int
    code = lib.ngSpice_Circ(circuit)
    if not any(line.strip().lower() == '.control' for line in lines_in) and not code:
        code = lib.ngSpice_Command(b'run')
    text = '\n'.join(lines)
    failure = any(term in text.lower() for term in ('error', 'fatal', 'unknown parameter', 'singular matrix', 'failed'))
    if exits:
        code = next((value for value in exits if value), 0)
    if handle:
        handle.close()
    return code or int(failure), text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('deck', type=Path)
    parser.add_argument('--dll')
    args = parser.parse_args()
    code, output = run(args.deck, args.dll)
    print(output)
    raise SystemExit(code)
