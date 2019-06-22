%{
#include <stdio.h>
#include <memory>
#include "ast.hpp"

extern int yylex();
extern int last_token_line;
extern int last_token_column;
static void yyerror(task_t** _, const char *message);

%}

%parse-param { task_t** result }
%define parse.error verbose
//%locations %define api.pure full
//%define api.value.type {int}
%token <int_literal> NAT
%token LPAREN "("
%token RPAREN ")"
%token COMMA ","
%token B "B"
%token F "F"
%token L "L"
%token X "X"
%token SEMICOLON ";"
%token SHARP "#"

%start task

%union {
    point_t             point;
    booster_code_t      booster_code;
    booster_location_t  booster_location;
    map_t               *map;
    boosters_t          *boosters;
    obstacles_t         *obstacles;
    task_t              *task;
    int                 int_literal;
}

%type <booster_code>     booster_code
%type <booster_location> booster_location
%type <point>       point
%type <map>        map
%type <obstacles>  obstacles obstacles1
%type <boosters>   boosters boosters1
%type <task>       task

%%

point:
    "(" NAT "," NAT ")" { $$ = { $$.x = $2, $$.y = $4 }; }
    ;

map:
      point             { $$ = new map_t(); $$->push_back($1); }
    | map "," point     { $1->push_back($3); $$ = $1; }
    ;

booster_code:
      "B" { $$ = CODE_B; }
    | "F" { $$ = CODE_F; }
    | "L" { $$ = CODE_L; }
    | "X" { $$ = CODE_X; }
    ;

booster_location:
    booster_code point { $$ = { .code = $1, .location = $2 }; }
    ;

obstacles:
      %empty      { $$ = new obstacles_t(); }
    | obstacles1  { $$ = $1; }
    ;

obstacles1:
      map                   { $$ = new obstacles_t(); $$->push_back($1); }
    | obstacles1 ";" map    { $1->push_back($3); $$ = $1; }
    ;

boosters:
      %empty     { $$ = new boosters_t(); }
    | boosters1  { $$ = $1; }
    ;

boosters1:
      booster_location                  { $$ = new boosters_t(); $$->push_back($1); }
    | boosters1 ";" booster_location    { $$ = $1; $$->push_back($3); }

task:
    map "#" point "#" obstacles "#" boosters
    { $$ = new task_t();
      $$->map = *$1;
      $$->initial_position = $3;
      $$->obstacles = *$5;
      $$->boosters = *$7;
      *result = $$;
    }
    ;

%%

static void yyerror (task_t** _, const char *message) {
  fprintf (stderr, "syntax error at line %i, col %i: %s\n",
           last_token_line,
           last_token_column,
           message);
  exit(1);
}