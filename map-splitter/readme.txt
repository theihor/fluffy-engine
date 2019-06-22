In order to compile the app the following packages are necessary:
- cmake
- flex
- bison
- libcgal-dev

Instructions for compilation:

mkdir build
cd build
cmake ../src
make

Afterwards just type "make".

Running the splitter:

./map_splitter <task-input-file> <json-output-file> <svg-output-file>
