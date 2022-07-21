#ifndef BAR_H_
#define BAR_H_

#include <string>
#include <iostream>
#include <ctime>

class Bar {
public:
    void print_header();
    void print_bar();
    void print_trailer();
    void set_total(size_t total) { total_events = total; }

    void operator++(int) { n_proc_events++; }
    size_t operator() () { return n_proc_events; }
    void pass() { passed_events++; }

private:

    size_t passed_events = 0;
    size_t total_events = 0;
    size_t n_proc_events = 0;

    const size_t barWidth  = 75;
    size_t freq = 10000;
    time_t start_time;
};

#endif // BAR_H_
