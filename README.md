# AVR UART ADC Logger

## Engineering evidence

- `tools/decode_uart_log.py` validates the firmware's `ADC=123` UART lines and reports mean, range, and noise level.
- Run `python tools/decode_uart_log.py capture.log` to turn a captured UART session into measurable results.
- The firmware and analysis path demonstrate embedded acquisition plus a practical host-side observability workflow.

## Objective

Sample an analog channel on an ATmega328P and stream the results over UART without the Arduino core. The project demonstrates bare-metal ADC and USART setup together with a simple blocking transmit path.

## Strategy

- Configure the ADC for free-running or single conversion on ADC0 (PC0).
- Configure USART0 for 9600 baud at 16 MHz with 8N1.
- In the main loop, start a conversion, wait for completion, convert the 10-bit result to decimal ASCII, and transmit it with a newline.
- Keep the code small enough that every register write is visible.

## What worked

- Free-running mode with a modest prescaler produced a continuous stream of samples without software triggers.
- A simple integer-to-ASCII conversion avoided the need for printf and kept the binary under 1 KB.
- The Arduino Uno bootloader still accepted the hex, so no external programmer was required for development.

## What failed and how it was resolved

- Incorrect UBRR value produced garbage characters. Resolution: calculate UBRR = F_CPU / (16 * baud) - 1 and verify with a scope or known-good terminal.
- Leaving the ADC disabled after the first sample stopped further conversions. Resolution: keep ADEN set and either re-set ADSC for single conversion or enable free-running (ADFR / ADATE).
- Transmitting while the previous byte was still shifting out overwrote the data register. Resolution: wait for UDRE before writing UDR.

## Engineering principles and frameworks used

- Bare-metal AVR peripheral programming.
- Polling-based driver design for simplicity.
- Minimal runtime and no C library formatted I/O.
- Explicit baud-rate calculation from the system clock.

## Hardware

- ATmega328P on Arduino Uno or equivalent
- Potentiometer or sensor on A0 (PC0)
- USB-serial connection for the UART output

## Build

```
make
make flash
```

## Possible extensions

- Switch to interrupt-driven UART transmit with a ring buffer.
- Add a simple digital filter (moving average) before printing.
- Timestamp each sample using Timer1.
