#ifndef LOGGING_H_
#define LOGGING_H_

#define LOG_WARN LOG_S(WARNING)
#define LOG_FUNC LOG_S(8)
#define LOG_EVENT LOG_S(7)
#define LOG_POST LOG_S(1)

#define LOG_FUNC_IF(X) LOG_IF_S(8, X)
#define LOG_EVENT_IF(X) LOG_IF_S(7, X)
#define LOG_POST_IF(X) LOG_IF_S(1, X)


#include"analysis_suite/skim/interface/loguru.hpp"

#endif // LOGGING_H_
