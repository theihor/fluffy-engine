#include <vector>
#include <memory>

struct point_t {
    int x;
    int y;
};

enum booster_code_t {
    CODE_B, CODE_F, CODE_L, CODE_X
};

struct booster_location_t {
    booster_code_t code;
    point_t location;
};

typedef std::vector<point_t> map_t;
typedef std::vector<booster_location_t> boosters_t;
typedef std::vector<map_t*> obstacles_t;

struct task_t {
    map_t map;
    point_t initial_position;
    boosters_t boosters;
    obstacles_t obstacles;
};
