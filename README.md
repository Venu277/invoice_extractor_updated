# MicroOS

A minimal x86_64 operating system kernel written in Rust. It boots in QEMU and prints text to the screen through the VGA text buffer.

> **Status:** Early-stage learning project. Current functionality is limited to booting and printing text.

## Features

- Written in `no_std` Rust with no operating system underneath it
- Custom x86_64 target specification (`x86_64-micro_os.json`)
- Boots through the `bootloader` crate (v0.9.35) and runs under QEMU
- Text output via the VGA text buffer

## Project Structure

```
micro_os/
├── .cargo/              # Cargo build configuration for the custom target
├── src/                 # Kernel source code
├── Cargo.toml           # Package manifest and dependencies
├── Cargo.lock
├── rust-toolchain.toml  # Pins the Rust nightly toolchain
├── x86_64-micro_os.json # Custom target specification
└── README.md
```

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Rust (via rustup) | `nightly-2025-06-01` | Builds the kernel. Pinned in `rust-toolchain.toml`. |
| `rust-src` component | Matches toolchain | Needed to build `core` for the custom target |
| `llvm-tools-preview` component | Matches toolchain | Needed by `bootimage` to assemble the bootable image |
| `bootimage` | `0.10.3` | Combines the kernel with the bootloader into a bootable disk image |
| QEMU | Any recent version | Emulates an x86_64 machine to run the OS |

## Setup

**Step 1: Install Rust with rustup**

If you don't have rustup, install it from [rustup.rs](https://rustup.rs). The pinned nightly toolchain is installed automatically the first time you build inside this project because of `rust-toolchain.toml`.

**Step 2: Add the required Rust components**

From inside the project folder:

```bash
rustup component add rust-src llvm-tools-preview
```

**Step 3: Install bootimage**

```bash
cargo install bootimage --version 0.10.3
```

**Step 4: Install QEMU**

- **Ubuntu/Debian:** `sudo apt install qemu-system-x86`
- **macOS (Homebrew):** `brew install qemu`
- **Windows:** Download the installer from [qemu.org](https://www.qemu.org/download/#windows) and add its `bin` folder to your `PATH`.

Verify the install with:

```bash
qemu-system-x86_64 --version
```

## Build and Run

From the project root:

```bash
cargo run
```

This compiles the kernel, creates the bootable image, and launches it in QEMU. You should see the text printed on the VGA output in the QEMU window.

## Troubleshooting

- **Build fails with target or ABI errors:** The `bootloader` 0.9.35 target file needed manual edits: `target-pointer-width` and `target-c-int-width` had to be strings, and `rustc-abi = "x86-softfloat"` had to be added. See the Notes section below.
- **`cargo run` cannot find `bootimage`:** Make sure you ran Step 3 and that `~/.cargo/bin` is on your `PATH`.
- **QEMU window does not open:** Confirm `qemu-system-x86_64` is installed and on your `PATH`.

## Notes

- The toolchain is pinned in `rust-toolchain.toml`. Do not update it without retesting the build.
- The `bootloader` crate's `x86_64-bootloader.json` target file required the manual edits described above.

## Roadmap

The long-term goal is to build a complete, working micro operating system that runs on virtually any desktop by the end of Semester 3.

## Resources

- [Writing an OS in Rust](https://os.phil-opp.com/): the tutorial this kind of project is usually based on, which covers VGA output, bootimage, and QEMU setup.

## License

Add a license here (for example, MIT) if you plan to share or reuse this project.
