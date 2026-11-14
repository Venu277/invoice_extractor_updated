# MicroOS — Progress Log

## Current Step: Step 0 — Baseline & Hygiene ✅

**Date:** 2026-11-14

---

## What Is Done

### Pre-existing (verified in Step 0)
- Rust kernel, x86_64, BIOS boot via `bootloader = "0.9"` + `bootimage 0.10.3`
- Pinned toolchain: `nightly-2025-06-01` (rust-src, llvm-tools-preview)
- Custom target `x86_64-micro_os.json`: 64-bit, softfloat, lld linker, panic=abort
- bootloader 0.9.35 target JSON hand-patched (pointer-width strings + rustc-abi)
- VGA `println!` macro, serial `serial_println!` macro
- Library/binary split: `src/lib.rs` + `src/main.rs`
- Custom test framework with `isa-debug-exit` (exit code 33 = success)
- IDT with breakpoint handler and page fault handler (`src/interrupts.rs`)

### Added in Step 0
- Fixed duplicate `#[cfg(test)] _start` in `src/lib.rs` (compilation error)
- `README.md` — full project overview including honest scope
- `PROGRESS.md` — this file
- `BOOT_TIMES.md` — boot time measurement table
- `docs/` directory created
- `docs/STEP_00_baseline.md` — step documentation
- `.gitignore` updated: `target/`, `*.iso`, `*.vmdk`, `*.img`, `disk.img`
- TSC-based boot timer added to `src/main.rs` (prints `BOOT_TIME_MS=<n>` on serial)
- Git remote `updated` added pointing to `micro-os` branch

---

## Verification Evidence (Step 0)

```
cargo build  →  Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.47s
cargo test   →  Running 4 tests
                micro_os::interrupts::test_breakpoint_exception...  [ok]
                micro_os::trivial_assertion...                       [ok]
                micro_os::vga_buffer::test_println_many...           [ok]
                micro_os::vga_buffer::test_println_simple...         [ok]
```

---

## Known Issues / Warnings

1. **OneDrive incremental cache:** `warning: hard linking files in the incremental
   compilation cache failed` — caused by OneDrive locking files. Workaround:
   build proceeds anyway (falls back to copying). Real fix: move project to
   `C:\dev\micro_os`. **Recommend but do not force** — ask user first.

2. **TSC calibration:** The TSC boot timer reads the TSC counter at `_start` and
   again after `init()`. Without PIT/RTC calibration the value is in raw TSC
   ticks, not milliseconds. Conversion added using a fixed estimate of
   ~2 GHz (500 ps/tick) — will be properly calibrated in Step 1 when PIT is set up.

3. **No GDT/TSS:** Double-fault will triple-fault the CPU. This is Step 1.

4. **No PIC remap:** Timer and keyboard IRQs still map to CPU exception vectors
   0x08–0x0F. This is Step 1.

5. **laptop_hardware.txt is missing.** Required for Step 8. The user must provide
   it before we reach Step 8.

---

## Decisions Made

| Decision | Chosen | Reason |
|----------|--------|--------|
| Toolchain pin | nightly-2025-06-01 | Already working; do not change casually |
| Bootloader | 0.9 (BIOS MBR) | Already integrated; UEFI migration is Step 8 |
| Allocator | TBD (Step 2) | linked-list or fixed-size-block |
| Package exec model | TBD (Step 9) | ring-3 ELF loader vs. WASM; await user approval |
| WiFi driver | Simulated (Step 7) | Real chipset needs bare metal + firmware |

---

## Next Step: Step 1 — Robust Interrupts

- GDT + TSS with separate double-fault stack (IST slot 0)
- Remap PIC 8259 to offsets 32/40
- Timer IRQ0 and keyboard IRQ1 handlers with EOI
- Lock-free scancode queue; process scancodes outside the interrupt handler
- Tests: breakpoint (existing), double-fault stack-overflow (separate test binary)
