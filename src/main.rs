#![no_std]
#![no_main]

mod vga_buffer;

use core::panic::PanicInfo;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    println!("==============================");
    println!("   MicroOS v0.2 - written in Rust");
    println!("==============================");
    println!("Kernel booted successfully!");
    println!("1 + 2 = {}", 1 + 2);

    loop {
        x86_64::instructions::hlt();
    }
}

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    println!("KERNEL PANIC: {}", info);
    loop {
        x86_64::instructions::hlt();
    }
}