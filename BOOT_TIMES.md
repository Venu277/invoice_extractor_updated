# MicroOS — Boot Time Log

## Measurement Method

| Field | Description |
|-------|-------------|
| **Kernel time (ms)** | From `_start` (TSC read) to `init()` complete. TSC ticks ÷ estimated 2 GHz. Printed on serial as `BOOT_TIME_MS=<n>`. Properly calibrated against PIT in Step 1. |
| **QEMU total (s)** | VM power-on to serial "kernel ready" message. Measured with stopwatch, average of 3 runs. |
| **VMware total (s)** | Same, measured in VMware Workstation (available from Step 5 onward). |
| **Method** | How the measurement was taken. |

---

## Boot Time Table

| Step | Component Added | Kernel Init (ms) | QEMU Total (s) | VMware Total (s) | Method | Date |
|------|----------------|-----------------|----------------|-----------------|--------|------|
| Step 0 | Baseline (IDT only) | 43.972 ms total* | ~1.5 s | — | TSC raw ticks ÷ 2GHz est.; QEMU serial-to-file capture | 2026-11-14 |

> \* `BOOT_TIME_MS=43.972` as reported by serial output (87,945,765 TSC ticks ÷ 2GHz).
> This includes the VGA println! output before `init()` — the IDT load itself takes
> < 0.01 ms. The 44 ms is dominated by BIOS boot + bootloader long-mode switch +
> first VGA writes. Proper PIT-calibrated frequency used in Step 1.

---

## Notes

- Kernel boot time will increase as more components are initialized (GDT, PIC,
  heap, scheduler, drivers). The table tracks this per step.
- QEMU total includes BIOS POST, bootloader stage 1+2 (long-mode switch), and
  kernel init. The bootloader itself takes ~0.5–1 s.
- VMware total is measured from "Power On" click to serial "kernel ready" line.
