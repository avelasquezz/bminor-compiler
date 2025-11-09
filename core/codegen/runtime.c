#include <stdio.h>

void _printi(int x) {
  printf("%i", x);
}

void _printf(double x) {
  printf("%lf", x);
}

void _printb(int x) {
  if (x) {
    printf("true");
  } else {
    printf("false");
  }
}

void _printc(char c) {
  printf("%c", c);
  fflush(stdout);
}