// A minimal unit-test harness: one executable per concern, each registered
// with CTest.
//
//   TEST(name) { CHECK(expr); CHECK_EQ(expected, actual); CHECK_STR(expected, actual); }
//   int main(void) { RUN(name); return TEST_RESULT(); }
#pragma once

#include <stdio.h>
#include <string.h>

static int test_failures;
static int test_checks;

#define TEST(name) static void name(void)

#define RUN(name)                                                               \
    do {                                                                        \
        int before_ = test_failures;                                            \
        name();                                                                 \
        printf("%s %s\n", test_failures == before_ ? "ok  " : "FAIL", #name);   \
    } while (0)

#define CHECK(expr)                                                             \
    do {                                                                        \
        test_checks++;                                                          \
        if (!(expr)) {                                                          \
            test_failures++;                                                    \
            fprintf(stderr, "%s:%d: CHECK(%s) failed\n", __FILE__, __LINE__, #expr); \
        }                                                                       \
    } while (0)

#define CHECK_EQ(expected, actual)                                              \
    do {                                                                        \
        long long e_ = (long long)(expected), a_ = (long long)(actual);         \
        test_checks++;                                                          \
        if (e_ != a_) {                                                         \
            test_failures++;                                                    \
            fprintf(stderr, "%s:%d: expected %s = %lld ($%llX), got %lld ($%llX)\n", \
                    __FILE__, __LINE__, #actual, e_, (unsigned long long)e_,    \
                    a_, (unsigned long long)a_);                                \
        }                                                                       \
    } while (0)

#define CHECK_STR(expected, actual)                                             \
    do {                                                                        \
        const char *e_ = (expected), *a_ = (actual);                            \
        test_checks++;                                                          \
        if (strcmp(e_, a_) != 0) {                                              \
            test_failures++;                                                    \
            fprintf(stderr, "%s:%d: expected %s =\n\"%s\"\ngot\n\"%s\"\n",      \
                    __FILE__, __LINE__, #actual, e_, a_);                       \
        }                                                                       \
    } while (0)

#define TEST_RESULT()                                                           \
    (printf("%d checks, %d failed\n", test_checks, test_failures), test_failures != 0)
