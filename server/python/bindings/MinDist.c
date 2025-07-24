#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

// Define the keyboard layout dynamically
#define ROWS 4
#define COLS 24

char keyboard[ROWS][COLS] = {
    {'1', '!', '2', '@', '3', '#', '4', '$', '5', '%', '6', '^', '7', '&', '8', '*', '9', '(', '0', ')', '-', '_', '='},
    {'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '{', '[', '}', ']', '\\', '|'},
    {'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', ':', '"', '\''},
    {'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '<', '.', '>', '/', '?'}
};

typedef struct {
    int x;
    int y;
} Position;

Position get_position(char ch) {
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            if (keyboard[i][j] == ch) {
                Position pos = {j, i};
                return pos;
            }
        }
    }
    Position invalid = {-1, -1};
    return invalid;
}

int minDistance(char *word1, char *word2) {
    int m = strlen(word1), n = strlen(word2);
    int *prev = calloc(n + 1, sizeof(int)), *curr = calloc(n + 1, sizeof(int));

    for (int j = 0; j <= n; j++)
        prev[j] = j;

    for (int i = 1; i <= m; i++) {
        curr[0] = i;
        for (int j = 1; j <= n; j++) {
            if (word1[i - 1] == word2[j - 1])
                curr[j] = prev[j - 1];
            else
                curr[j] = 1 + fmin(fmin(prev[j], curr[j - 1]), prev[j - 1]);
        }
        int *temp = prev;
        prev = curr;
        curr = temp;
    }
    int result = prev[n];
    free(prev);
    free(curr);
    return result;
}

double keyboardDist(char *word1, char *word2) {
    double dist = 0;
    int len = fmin(strlen(word1), strlen(word2));
    for (int i = 0; i < len; i++) {
        Position p1 = get_position(word1[i]);
        Position p2 = get_position(word2[i]);
        if (p1.x == -1 || p2.x == -1) continue;

        dist += sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2));
    }
    return dist;
}
