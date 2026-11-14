# MicroOS

A hobby x86_64 operating system kernel written in Rust, built from scratch as a
learning project. It currently boots in QEMU and is being developed step-by-step
toward a VMware-bootable OS with networking, storage, and a package manager.

> **Honest Scope:** See the [Honest Scope](#honest-scope) section below.

---

## Current Status

| Step | Name | Status |
|------|------|--------|
| Step 0 | Baseline, hygiene, TSC boot timer | ✅ Done |
| Step 1 | GDT/TSS, PIC, timer/keyboard IRQs | 🔲 Next |
| Step 2 | Paging, frame allocator, heap, alloc | 🔲 Planned |
| Step 3 | Async executor, shell, system clock | 🔲 Planned |
| Step 4 | Storage, file system | 🔲 Planned |
| Step 5 | ISO packaging, VMware boot | 🔲 Planned |
| Step 6 | LAN networking (e1000, smoltcp) | 🔲 Planned |
| Step 7 | WiFi layer | 🔲 Planned |
| Step 8 | Laptop hardware compatibility | 🔲 Planned |
| Step 9 | Package manager `apt` / `aptitude` | 🔲 Planned |
| Step 10 | Package store `snap` | 🔲 Planned |
| Step 11 | Final integration and presentation | 🔲 Planned |

See [PROGRESS.md](PROGRESS.md) for the current detailed status.

---

## Honest Scope

This project builds **MicroOS-native** tools that share command names and formats
with Linux, but are **not** Linux-compatible:

- **`apt` / `aptitude`**: Parses real Debian `Packages` index files and `.deb`
  archive format (ar + control.tar + data.tar), implements dependency resolution
  and a dpkg-style status database — but packages must be built for MicroOS.
  Prebuilt Debian/Ubuntu `.deb` binaries will **not** run; they require Linux
  kernel ABI, glibc, and ELF dynamic linking against the Linux dynamic linker.

- **`snap` store**: A snap-style package store with its own manifest format and
  HTTP index. This is **not** real snapd/squashfs. Real Snap packages require
  snapd, squashfs-tools, AppArmor, and the Linux kernel.

- **WiFi in VMware**: The host's WiFi NIC is presented as an Ethernet device to
  the guest. A real chipset driver (e.g. Intel iwlwifi) cannot be exercised in a
  VM. The WiFi layer is implemented with a clean driver trait so a real driver
  can be added when running on bare metal.

- **No Linux ABI**: MicroOS has its own syscall interface. Linux ELF binaries will
  not run.

---

## Project Structure

```
micro_os-main/
├── .cargo/              # Cargo build config (custom target, build-std)
├── src/
│   ├── lib.rs           # Library root: test framework, init, hlt_loop
│   ├── main.rs          # Kernel entry point (_start)
│   ├── vga_buffer.rs    # VGA text-mode driver and println! macro
│   ├── serial.rs        # UART serial port driver and serial_println! macro
│   └── interrupts.rs    # IDT: breakpoint + page fault handlers
├── docs/                # Per-step documentation
├── Cargo.toml           # Package manifest
├── rust-toolchain.toml  # Pins nightly-2025-06-01
├── x86_64-micro_os.json # Custom target spec (no_std, softfloat, ld.lld)
├── PROGRESS.md          # Current state, known issues, decisions
├── BOOT_TIMES.md        # Boot time measurements per step
└── README.md            # This file
```

---

## Prerequisites

| Tool | Version / Notes |
|------|----------------|
| Rust (rustup) | Toolchain pinned to `nightly-2025-06-01` via `rust-toolchain.toml` |
| `rust-src` component | Required to build `core` for the custom target |
| `llvm-tools-preview` | Required by `bootimage` to objcopy the kernel binary |
| `bootimage` | 0.10.3 — install with `cargo install bootimage --version 0.10.3` |
| QEMU | Any recent x86_64 build — on Windows add to PATH: `C:\Program Files\qemu` |

---

## Build and Run

```powershell
# From the project root on Windows PowerShell:
$env:PATH += ";C:\Program Files\qemu"

cargo build          # Compile the kernel
cargo test           # Run all tests in QEMU (custom test framework)
cargo run            # Boot in QEMU (serial output visible in terminal)
```

---

## Toolchain Patch Notes

**bootloader 0.9.35 target file hand-patch** (required; re-apply if Cargo clears
the registry):

File: `%USERPROFILE%\.cargo\registry\src\...\bootloader-0.9.35\x86_64-bootloader.json`

Changes made:
1. `"target-pointer-width"` changed from integer `64` to string `"64"`
2. `"target-c-int-width"` changed from integer `32` to string `"32"`
3. Added `"rustc-abi": "x86-softfloat"`

These match the `x86_64-micro_os.json` custom target. Without this patch the
bootloader crate fails to compile with an ABI mismatch error.

---

## OneDrive Warning

> **Recommendation:** Move the project folder out of OneDrive to avoid sync
> slowdowns and incremental-cache `Access Denied` errors:
>
> ```powershell
> Move-Item "C:\Users\Venugopal\OneDrive\Desktop\micro_os-main" "C:\dev\micro_os"
> ```
>
> Ask me before moving; it will change all paths in scripts.

---

## Resources

- [Writing an OS in Rust](https://os.phil-opp.com/) — the tutorial series this
  project is based on
- [OSDev Wiki](https://wiki.osdev.org/) — reference for x86_64 internals

## License

MIT (add `LICENSE` file when sharing publicly)
