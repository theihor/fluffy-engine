#include <stdio.h>

#include <iostream>
#include <fstream>
#include <iterator>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Boolean_set_operations_2.h>
#include <CGAL/Polygon_set_2.h>
#include <CGAL/Polygon_vertical_decomposition_2.h>

#include "ast.hpp"
#include "task_parser.hpp"

using std::to_string;
using std::cout;
using std::cerr;
using std::vector;
using std::string;
using std::back_inserter;

extern FILE* yyin;

typedef CGAL::Exact_predicates_exact_constructions_kernel K;
typedef K::Point_2 cg_point;
typedef CGAL::Polygon_2<K> cg_polygon;
typedef CGAL::Polygon_with_holes_2<K> cg_polygon_with_holes;
typedef CGAL::Polygon_set_2<K> cg_polygon_set;
typedef CGAL::Polygon_vertical_decomposition_2<K> cg_vertical_decomposition;

string to_string(point_t &point) {
    string str;
    str += "(";
    str += to_string(point.x);
    str += ",";
    str += to_string(point.y);
    str += ")";
    return str;
}

string to_string(booster_location_t &booster) {
    string str;
    switch (booster.code) {
        case CODE_B: str += "B"; break;
        case CODE_F: str += "F"; break;
        case CODE_L: str += "L"; break;
        case CODE_X: str += "X"; break;
    }
    str += to_string(booster.location);
    return str;
}

cg_polygon polygon_for_map(map_t &map) {
    auto points = vector<cg_point>();
    for (auto it = map.begin(); it != map.end(); ++it) {
        points.push_back(cg_point(it->x, it->y));
    }
    return cg_polygon(points.begin(), points.end());
}

void polygons_for_task(task_t &task, vector<cg_polygon_with_holes> &out) {
    auto set = cg_polygon_set();
    auto map_poly = polygon_for_map(task.map);
    set.insert(map_poly);
    for (auto it = task.obstacles.begin(); it != task.obstacles.end(); ++it) {
        set.difference(polygon_for_map(**it));
    }
    set.polygons_with_holes(back_inserter(out));
}

void split_into_convex_polygons(vector<cg_polygon_with_holes> &polygons, vector<cg_polygon> &out) {
    auto decomposition = cg_vertical_decomposition();
    for (auto it = polygons.begin(); it != polygons.end(); ++it) {
        decomposition(*it, back_inserter(out));
    }
}

void show_map(const char *indent, map_t &map) {
    for (auto it = map.begin(); it != map.end(); ++it) {
        cout << indent << to_string(*it) << "\n";
    }
}

void show_ast(task_t &task) {
    cout << "task:\n";
    cout << "  initial_position:\n";
    cout << "    " << to_string(task.initial_position) << "\n"; 
    cout << "  map:\n";
    show_map("    ", task.map);
    cout << "  boosters:\n";
    for (auto it = task.boosters.begin(); it != task.boosters.end(); ++it) {
        cout << "    " << to_string(*it) << "\n";
    }
    cout << "  obstacles:\n";
    int n = 0;
    for (auto it = task.obstacles.begin(); it != task.obstacles.end(); ++it) {
        cout << "    " << n << ":\n";
        show_map("      ", **it);
        ++n;
    }
}

class poly_visitor {
public:
    virtual void header() {};
    virtual void trailer() {};
    virtual void start_poly() {};
    virtual void end_poly() {};
    virtual void vertex(cg_point &v) {};
};

void visit_polys(vector<cg_polygon> &polys, poly_visitor &visitor) {
    visitor.header();
    for (auto it_poly = polys.begin(); it_poly != polys.end(); ++it_poly) {
        visitor.start_poly();
        cg_polygon &poly = *it_poly;
        for (auto it_vertex = poly.vertices_begin(); it_vertex != poly.vertices_end(); ++it_vertex) {
            visitor.vertex(*it_vertex);
        }
        visitor.end_poly();
    }
    visitor.trailer();
}

class json_output_visitor: public poly_visitor {
    std::fstream &json;
public:
    json_output_visitor(std::fstream &_json) : json(_json) {}
    virtual void header() {
        json << "{\n";
        json << "  \"polygons\": [\n";
    }
    virtual void trailer() {
        json << "  ]\n";
        json << "}\n";
    }
    virtual void start_poly() {
        json << "    [\n";
    }
    virtual void end_poly() {
        json << "    ],\n";
    }
    virtual void vertex(cg_point& v) {
        json << "      { \"x\": " << v.x() <<  ", \"y\": " << v.y() << " },\n";
    }
};


class bb_visitor: public poly_visitor {
public:
    int min_x = 0;
    int max_x = 0;
    int min_y = 0;
    int max_y = 0;
    virtual void vertex(cg_point& v) {
        int x = CGAL::to_double(v.x());
        int y = CGAL::to_double(v.y());
        if (x < min_x) min_x = x;
        if (x > max_x) max_x = x;
        if (y < min_y) min_y = y;
        if (y > max_y) max_y = y;
    }
};

const char * svg_colors[] = {
    "black", "grey", "darkgrey"
};

class svg_output_visitor: public poly_visitor {
    std::fstream &svg;
    bb_visitor &bb;
    int color_index = 0;
public:
    svg_output_visitor(std::fstream &_svg, bb_visitor &_bb) : svg(_svg), bb(_bb) {}
    virtual void header() {
        svg << "<svg viewBox=\"" 
            << bb.min_x << " " << bb.min_y << " "
            << bb.max_x << " " << bb.max_y << "\" "
            << "xmlns=\"http://www.w3.org/2000/svg\">\n";
    }
    virtual void trailer() {
        svg << "</svg>\n";
    }
    virtual void start_poly() {
        svg << "  <polygon "
            << "fill=\"none\" stroke=\""
            << svg_colors[color_index]
            << "\" points=\"";
        color_index = (color_index + 1) % 3;
    }
    virtual void end_poly() {
        svg << "\"/>\n";
    }
    virtual void vertex(cg_point& v) {
        svg << v.x() <<  "," << v.y() << " ";
    }
};

int main(int argc, char **argv) {
    if (argc != 4) {
        cerr << "usage: <task-file-name> <output-file-json> <output-file-svg>\n";
        return 1;
    }

    char *input_file = argv[1];
    char *output_file = argv[2];
    char *svg_file = argv[3];

    yyin = fopen(input_file, "r");
    if (yyin == NULL) {
        perror("Can't open input file");
        return 1;
    }
    task_t *task;
    yyparse(&task);
    show_ast(*task);
    fclose(yyin);

    vector<cg_polygon_with_holes> task_polys;
    vector<cg_polygon> convex_polys; 
    polygons_for_task(*task, task_polys);
    split_into_convex_polygons(task_polys, convex_polys);

    cout << "split into " << to_string(convex_polys.size()) << " convex parts\n";

    std::fstream json;
    std::fstream svg;
    json_output_visitor json_writer(json);
    bb_visitor bb;
    svg_output_visitor  svg_writer(svg, bb);

    json.open(output_file, std::ios_base::out);
    visit_polys(convex_polys, json_writer);
    json.close();

    visit_polys(convex_polys, bb);
    svg.open(svg_file, std::ios_base::out);
    visit_polys(convex_polys, svg_writer);
    svg.close();

    return 0;
}
