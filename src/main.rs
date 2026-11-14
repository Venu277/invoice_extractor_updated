#![no_std]
#![no_main]
#![feature(custom_test_frameworks)]
#![test_runner(micro_os::test_runner)]
#![reexport_test_harness_main = "test_main"]

use core::panic::PanicInfo;
use micro_os::println;

#[no_mangle]
pub extern "C" fn _start() -> ! {
    // TSC boot timer — read TSC as early as possible
    let tsc_start: u64 = unsafe { core::arch::x86_64::_rdtsc() };

    println!("==============================");
    println!("   MicroOS v0.2 - written in Rust");
    println!("==============================");
    println!("Kernel booted successfully!");
    micro_os::serial_println!("Serial port works too!");

    micro_os::init();

    // TSC after init() — compute elapsed ticks
    let tsc_end: u64 = unsafe { core::arch::x86_64::_rdtsc() };
    // Estimate: assume ~2 GHz TSC frequency (500 ps/tick)
    // 1 ms = 2_000_000 ticks at 2 GHz
    let ticks = tsc_end.wrapping_sub(tsc_start);
    let ms_est = ticks / 2_000_000;
    let us_est = (ticks / 2_000) % 1_000;
    micro_os::serial_println!(
        "BOOT_TIME_MS={}.{:03} (raw TSC ticks={}, ~2GHz est.)",
        ms_est, us_est, ticks
    );

    x86_64::instructions::interrupts::int3();

    println!("It did not crash!");
    micro_os::serial_println!("Kernel ready. Interrupts OK.");

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