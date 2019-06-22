%{

#include "ast.hpp"
#include "task_parser.hpp"

#include <stdlib.h>

int last_token_line = 1;
int last_token_column = 1;

#define YY_USER_ACTION { last_token_column += yyleng; }

%}

%option noyywrap

%%

[0-9]+          yylval.int_literal = atoi(yytext); return NAT;
\(              return LPAREN;
\)              return RPAREN;
\,              return COMMA;
B               return B;
F               return F;
L               return L;
X               return X;
\;              return SEMICOLON;
\#              return SHARP;
\n              last_token_column = 1; last_token_line += 1;

%%