#![no_std]
#![no_main]
#![feature(custom_test_frameworks)]
#![test_runner(micro_os::test_runner)]
#![reexport_test_harness_main = "test_main"]

use core::panic::PanicInfo;
use micro_os::println;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    println!("==============================");
    println!("   MicroOS v0.2 - written in Rust");
    println!("==============================");
    println!("Kernel booted successfully!");
    micro_os::serial_println!("Serial port works too!");

    micro_os::init();

    x86_64::instructions::interrupts::int3();

    println!("It did not crash!");

    #[cfg(test)]
    test_main();

    micro_os::hlt_loop();
}

#[cfg(not(test))]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    println!("KERNEL PANIC: {}", info);
    micro_os::hlt_loop();
}

#[cfg(test)]
#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    micro_os::test_panic_handler(info)
}