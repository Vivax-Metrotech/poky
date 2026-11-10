#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the actual RX completion body before/after the public backport.

DMA and tty peers are deterministic stubs. This is not a kernel concurrency,
UART hardware, timing, shutdown-latency or electrical qualification.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


PREFIX = r'''
#include <stdint.h>
#include <string.h>
typedef uint32_t u32;
typedef int dma_cookie_t;
struct dma_chan { int unused; };
struct dma_tx_state { int residue; int in_flight_bytes; };
struct tty_port { int unused; };
struct omap8250_priv { unsigned habit; };
struct uart_8250_dma {
    struct dma_chan *rxchan;
    int rx_cookie, rx_size, rx_running;
    unsigned char *rx_buf;
};
struct uart_8250_port {
    struct uart_8250_dma *dma;
    struct {
        void *private_data, *dev;
        struct { struct tty_port port; } *state;
        struct { int rx, buf_overrun; } icount;
    } port;
};
static int residue, terminations, copied, flips;
#define UART_HAS_RHR_IT_DIS 1
#define UART_OMAP_IER2 2
#define UART_OMAP_IER2_RHR_IT_DIS 4
#define dev_err(dev, message) ((void)(dev))
static u32 serial_in(struct uart_8250_port *p, int reg)
{ (void)p; (void)reg; return 0; }
static void serial_out(struct uart_8250_port *p, int reg, u32 value)
{ (void)p; (void)reg; (void)value; }
static int dmaengine_tx_status(struct dma_chan *chan, int cookie, struct dma_tx_state *state)
{
    (void)chan; (void)cookie;
    if (state) { state->residue = residue; state->in_flight_bytes = 0; }
    return 0;
}
static void dmaengine_terminate_async(struct dma_chan *chan)
{ (void)chan; ++terminations; }
static void cpu_relax(void) {}
static int tty_insert_flip_string(struct tty_port *port, unsigned char *buffer, int count)
{ (void)port; (void)buffer; copied += count; return count; }
static void tty_flip_buffer_push(struct tty_port *port)
{ (void)port; ++flips; }
'''

SUFFIX = r'''
int main(int argc, char **argv)
{
    struct dma_chan chan = {0};
    struct omap8250_priv priv = {0};
    struct uart_8250_dma dma = {.rxchan = &chan, .rx_size = 64, .rx_running = 1};
    struct uart_8250_port p = {.dma = &dma};
    struct { struct tty_port port; } state = {0};
    int expected_count = 0, expected_terminate = 0;
    if (argc != 2) return 1;
    p.port.private_data = &priv;
    p.port.state = (void *)&state;
    if (!strcmp(argv[1], "idle")) dma.rx_running = 0;
    else if (!strcmp(argv[1], "empty")) { residue = 64; expected_terminate = 1; }
    else if (!strcmp(argv[1], "partial")) { residue = 59; expected_count = 5; expected_terminate = 1; }
    else if (!strcmp(argv[1], "full")) expected_count = 64;
    else return 2;
    __dma_rx_do_complete(&p);
    if (dma.rx_running) return 42;
    if (terminations != expected_terminate || copied != expected_count ||
        p.port.icount.rx != expected_count || p.port.icount.buf_overrun || flips != 1) return 43;
    return 0;
}
'''


def body(text):
    return 'static void __dma_rx_do_complete(' + text.split(
        'static void __dma_rx_do_complete(', 1)[1].split('\nstatic void __dma_rx_complete(', 1)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel-source', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    patch = Path(__file__).resolve().parents[1] / 'files/0010-serial-8250-omap-clear-empty-rx-dma-completion.patch'
    relative = Path('drivers/tty/serial/8250/8250_omap.c')
    original = (args.kernel_source / relative).read_bytes()
    results, bodies = {}, {}
    with tempfile.TemporaryDirectory(prefix='omap8250-completion-') as temporary:
        root = Path(temporary)
        target = root / relative
        target.parent.mkdir(parents=True)
        target.write_bytes(original)
        for version in ('before', 'after'):
            if version == 'after':
                subprocess.run(['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', str(patch)],
                               cwd=root, check=True, capture_output=True, timeout=15)
            function = body(target.read_text())
            bodies[version] = hashlib.sha256(function.encode()).hexdigest()
            source, binary = root / (version + '.c'), root / version
            source.write_text(PREFIX + function + SUFFIX)
            subprocess.run([shutil.which('cc') or 'cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            '-O2', str(source), '-o', str(binary)], check=True, capture_output=True, timeout=30)
            results[version] = {case: subprocess.run([str(binary), case], timeout=5).returncode
                               for case in ('idle', 'empty', 'partial', 'full')}
    assert results['before'] == {'idle': 0, 'empty': 42, 'partial': 0, 'full': 0}, results
    assert all(value == 0 for value in results['after'].values()), results
    report = {'scope': 'actual-kernel-rx-completion-body-with-stubbed-dma-and-tty',
        'passed': True, 'upstream_commit': '061b627ba534230a18ec4d7251562af12325d06a',
        'original_file_sha256': hashlib.sha256(original).hexdigest(), 'body_sha256': bodies,
        'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(), 'exit_codes': results,
        'physical_uart_qualified': False, 'kernel_concurrency_qualified': False,
        'shutdown_latency_qualified': False}
    with args.report.open('x') as output:
        json.dump(report, output, sort_keys=True, indent=2)
        output.write('\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
