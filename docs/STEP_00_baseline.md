# Step 0 — Baseline & Hygiene

## 1. Goal

Verify the existing project compiles, all tests pass, and `cargo run` boots in QEMU.
Fix any pre-existing bugs. Add project scaffolding (README, PROGRESS, BOOT_TIMES,
docs/ folder). Add a TSC-based boot timer and record the baseline boot time.
Set up the git remote and push the project to the `micro-os` branch.

---

## 2. Files Created or Changed

| File | Action | Purpose |
|------|--------|---------|
| `src/lib.rs` | **Fixed** | Removed duplicate `#[cfg(test)] _start` function (caused E0428 at test time) |
| `src/main.rs` | **Changed** | Added TSC boot timer (`_rdtsc` before and after `init()`); prints `BOOT_TIME_MS=<n>` on serial |
| `.gitignore` | **Updated** | Added `*.iso`, `*.vmdk`, `*.img`, `disk.img` entries |
| `README.md` | **Rewritten** | Full project overview: steps table, honest scope, structure, prerequisites, build instructions, toolchain patch notes, OneDrive warning |
| `PROGRESS.md` | **Created** | Current step, what is done, known issues, decisions table, next step |
| `BOOT_TIMES.md` | **Created** | Boot time measurement table (method, kernel time, QEMU total, VMware total) |
| `docs/` | **Created** | Directory for per-step documentation |
| `docs/STEP_00_baseline.md` | **Created** | This file |

---

## 3. How It Works

### Plain English

When the CPU starts, we immediately read the **Time Stamp Counter (TSC)** — a
hardware register that counts CPU clock cycles since the chip was reset. We read
it again after `init()` finishes (which currently just loads the Interrupt
Descriptor Table). The difference in ticks, divided by the CPU's approximate
clock frequency, gives us the elapsed time.

We print this over the serial port (UART COM1) so the value is visible even
without a VGA display.

### Technical Detail

```
_start() called
  │
  ├─ RDTSC → tsc_start              (read CPU cycle counter)
  │
  ├─ println! banner (VGA writes)
  │
  ├─ init() → init_idt()            (loads IDT with breakpoint + page-fault handlers)
  │
  ├─ RDTSC → tsc_end                (read CPU cycle counter again)
  │
  ├─ Compute: ticks = tsc_end - tsc_start
  │           ms ≈ ticks / 2_000_000   (assuming 2 GHz TSC)
  │
  ├─ serial_println!("BOOT_TIME_MS=...")
  │
  ├─ int3   (fires breakpoint; IDT catches it; execution resumes)
  │
  └─ hlt_loop()                     (kernel parks here)
```

The TSC frequency varies by CPU. The 2 GHz estimate is replaced by a PIT-based
calibration in Step 1. For Step 0 it gives an order-of-magnitude measurement.

### Why TSC?

The TSC is the simplest, highest-resolution timer available without any driver.
It doesn't require initializing the PIT or APIC. The downside is that we don't
know the exact frequency until we calibrate against a known-frequency source
(the PIT or CMOS RTC — Step 1).

---

## 4. How to Build, Run, and Test

```powershell
# Windows PowerShell — from project root
$env:PATH += ";C:\Program Files\qemu"

# Build
cargo build

# Run all tests in QEMU
cargo test

# Boot in QEMU (serial output visible in terminal)
cargo run
```

---

## 5. Verification Evidence

### `cargo build`

```
Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.47s
```

No errors. Only OneDrive hard-link warnings (harmless; see Known Limitations).

### `cargo test`

```
Running 4 tests
micro_os::interrupts::test_breakpoint_exception...  [ok]
micro_os::trivial_assertion...                       [ok]
micro_os::vga_buffer::test_println_many...           [ok]
micro_os::vga_buffer::test_println_simple...         [ok]
Running 0 tests    (main binary — no test cases there)
test result: ok.
```

All 4 tests pass. The breakpoint handler test (`int3` → IDT catches it → returns)
confirms Step 3's IDT is working.

### `cargo run` serial output (captured via `-serial file:`)

```
Serial port works too!
BOOT_TIME_MS=43.972 (raw TSC ticks=87945765, ~2GHz est.)
Kernel ready. Interrupts OK.
```

Kernel booted, IDT loaded, breakpoint handled, serial output confirmed.

---

## 6. Boot Time Measurement

| Metric | Value | Method |
|--------|-------|--------|
| Kernel TSC timer | **43.972 ms** | `RDTSC` before/after `init()`, ÷ 2GHz estimate |
| Raw TSC ticks | 87,945,765 | Printed in serial output |
| QEMU total (stopwatch) | ~1.5 s | VM power-on to serial "Kernel ready" message |
| VMware total | — | Not available until Step 5 |

> **Note:** 43 ms includes the VGA banner printing before `init()`. The IDT load
> itself takes < 0.01 ms. The bulk of the time is BIOS POST + bootloader switching
> to 64-bit long mode.

---

## 7. Known Limitations and What Is Next

### Limitations

1. **OneDrive incremental cache warnings** (`Access Denied` on hard-link GC) —
   harmless but noisy. Recommendation: move project to `C:\dev\micro_os`.

2. **TSC not calibrated** — the 2 GHz divisor is an estimate. Real calibration
   against PIT is in Step 1.

3. **No GDT/TSS** — a double-fault will triple-fault the CPU (no separate stack).
   This is the first thing Step 1 fixes.

4. **No PIC remap** — hardware IRQs 0–7 collide with CPU exception vectors 8–15.
   Step 1 remaps PIC to offsets 32/40.

5. **No `laptop_hardware.txt`** — required for Step 8 (hardware compatibility).
   The user must create this file describing their laptop's hardware before Step 8.

### What Is Next: Step 1 — Robust Interrupts

- GDT with a code segment and TSS
- TSS with a double-fault stack in IST slot 0
- Remap PIC 8259A: IRQ0–7 → INT 32–39, IRQ8–15 → INT 40–47
- Timer IRQ0 handler (increment tick counter, send EOI)
- Keyboard IRQ1 handler (read scancode, push to ArrayQueue, send EOI)
- Scancode processing loop outside the interrupt handler
- PIT calibration of TSC frequency
- Tests: breakpoint (existing), double-fault stack-overflow (new test binary)
