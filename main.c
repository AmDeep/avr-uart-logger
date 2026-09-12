#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#define F_CPU 16000000UL
#define BAUD  9600UL
#define UBRR_VAL ((F_CPU / (16UL * BAUD)) - 1)

volatile uint16_t latest_adc = 0;

void usart_init(void) {
    UBRR0H = (uint8_t)(UBRR_VAL >> 8);
    UBRR0L = (uint8_t)UBRR_VAL;
    UCSR0B = (1 << TXEN0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

void usart_write(char c) {
    while (!(UCSR0A & (1 << UDRE0)));
    UDR0 = c;
}

void usart_print(const char *s) {
    while (*s) usart_write(*s++);
}

void usart_print_u16(uint16_t v) {
    char buf[6];
    uint8_t i = 5;
    buf[i] = '\0';
    do {
        buf[--i] = '0' + (v % 10);
        v /= 10;
    } while (v && i > 0);
    usart_print(&buf[i]);
}

void adc_init(void) {
    ADMUX  = (1 << REFS0); // AVcc, channel 0
    ADCSRA = (1 << ADEN) | (1 << ADATE) | (1 << ADIE)
           | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // free run + interrupt, /128
    ADCSRB = 0; // free running
    ADCSRA |= (1 << ADSC); // start first conversion
}

ISR(ADC_vect) {
    latest_adc = ADC;
}

int main(void) {
    usart_init();
    adc_init();
    sei();

    usart_print("AVR ADC logger ready\r\n");

    uint16_t last_printed = 0xFFFF;
    while (1) {
        uint16_t v = latest_adc;
        // print only when value changes meaningfully or every ~200 ms
        static uint16_t div = 0;
        if (++div >= 20 || (v > last_printed + 4) || (last_printed > v + 4)) {
            div = 0;
            last_printed = v;
            usart_print("ADC=");
            usart_print_u16(v);
            usart_print("\r\n");
        }
        _delay_ms(10);
    }
}
