#include <stdio.h>

void _printi(int x) {
  printf("%i\n", x);
}

void _printf(double x) {
  printf("%lf\n", x);
}

void _printb(int x) {
  if (x) {
    printf("true\n");
  } else {
    printf("false\n");
  }
}

void _printc(char c) {
  printf("%c", c);
  fflush(stdout);
}