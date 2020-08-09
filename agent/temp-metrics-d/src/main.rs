use std::{thread, time};

fn main() {
    let measurement_periodicity = time::Duration::from_secs(1);
    loop {
        println!("Measuring the temperature!");
        thread::sleep(measurement_periodicity);   
    }
}
