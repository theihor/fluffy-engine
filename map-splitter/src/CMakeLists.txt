cmake_minimum_required(VERSION 3.13)

project(map-splitter)

set(CMAKE_BUILD_TYPE Debug)
set(CGAL_DO_NOT_WARN_ABOUT_CMAKE_BUILD_TYPE TRUE)

find_package(FLEX)
find_package(BISON)
find_package(CGAL)

flex_target(task_scanner task_scanner.l ${CMAKE_CURRENT_BINARY_DIR}/task_lexer.cpp)
bison_target(task_parser task_parser.y ${CMAKE_CURRENT_BINARY_DIR}/task_parser.cpp
             VERBOSE bison.log
             COMPILE_FLAGS -d)

add_flex_bison_dependency(task_scanner task_parser)

add_executable(
    map_splitter
    map_splitter.cpp
    ${BISON_task_parser_OUTPUTS}
    ${FLEX_task_scanner_OUTPUTS}
    )

target_link_libraries(map_splitter CGAL::CGAL)
target_include_directories(map_splitter 
    PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/
    PRIVATE ${PROJECT_SOURCE_DIR}/
    )
