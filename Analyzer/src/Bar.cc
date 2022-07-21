#include "analysis_suite/Analyzer/interface/Bar.h"

#include <sstream>
#include <cmath>

void Bar::print_header()
{
    std::cout << "Total number of events: " << total_events << std::endl;
    start_time = time(NULL);
}

void Bar::print_bar()
{
    if (n_proc_events % freq != 0 && n_proc_events != total_events)
        return;

    // Setup progress bar
    float progress = float(n_proc_events)/total_events;

    std::string bar = "[";
    bar += std::string(int(floor(progress*barWidth)), '=');
    if (bar.size() <= barWidth) bar += ">";
    if (bar.size() <= barWidth)
        bar += std::string(int((barWidth+1)-bar.size()), ' ');
    bar += "] ";
    std::ostringstream ss;
    ss.precision(2);
    ss << std::fixed <<progress*100;
    bar += ss.str() + " %  ";

    std::cout << bar;
    size_t elapse = static_cast<size_t>(time(NULL) - start_time);
    int ratio = (n_proc_events) ? static_cast<int>(((float)n_proc_events)/elapse) : 0;
    std::cout << " (" << elapse << "s - " << ratio << "#/s)";
    std::cout << " (" << passed_events << "/" << n_proc_events << ")" << std::endl;

}

void Bar::print_trailer()
{
    std::cout << "Passed (" << passed_events << ") of total processed (" << n_proc_events << ")" << std::endl;
}
