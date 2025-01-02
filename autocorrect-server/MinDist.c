#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#define min(a, b) ((a) < (b) ? (a) : (b))
#define max(a, b) ((a) > (b) ? (a) : (b))
#define abs(a) ((a < 0) ? (-(a)) : (a))

int minDistance(char *word1, char *word2) {
    int m = strlen(word1);
    int n = strlen(word2);

    // Create a 2D array to store the edit distances
    int **cache = (int **)malloc((m + 1) * sizeof(int *));
    for (int i = 0; i <= m; i++) {
        cache[i] = (int *)malloc((n + 1) * sizeof(int));
    }

    // Initialize the base cases for the edit distance matrix
    for (int j = 0; j <= n; j++) {
        cache[m][j] = n - j;
    }
    for (int i = 0; i <= m; i++) {
        cache[i][n] = m - i;
    }

    /**
     * Work bottom-up. Start from the corner of the matrix and
     * calculate the edit distance operation changes depending
     * on the base cases initially and working all the way up.
     * Prioritize changes near the beginning by adding a weight
     * factor based on the position of the characters.
    **/
    for (int i = m - 1; i >= 0; i--) {
        for (int j = n - 1; j >= 0; j--) {
            if (word1[i] == word2[j]) {
                cache[i][j] = cache[i + 1][j + 1];
            } else {
                cache[i][j] = 1 + min(
                            cache[i + 1][j] + ((i + 1) / m),          // Delete  (weight based on i)
                            min(cache[i][j + 1] + ((j + 1) / n),      // Insert  (weight based on j)
                                cache[i + 1][j + 1] + (max(i + 1, j + 1) / max(m, n)))  // Replace (weight based on i and j)
                            );
            }
        }
    }

    // Store the result and free the memory
    int result = cache[0][0];
    for (int i = 0; i <= m; i++) {
        free(cache[i]);
    }
    free(cache);

    return result;
}


/*
 * The keyboardDist function is intended to find the Euclidian Distance between
 * a given letter and the target letter given a misspelling. This method is only
 * called for words that are the exact same length as a test. 
 */

double keyboardDist(char letter, char target) {
    char kb_arr[4][24] = { {'1', '!', '2', '@', '3', '#', '4', '$', '5', '%', '6', '^', '7', '&', '8', '*', '9', '(', '0', ')', '-', '_', '=', '+'},
                        {'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'o', 'p', '{', '[', '}', ']', '\\', '|'},
                        {'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', ':', '"', '\''},
                        {'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '<', '.', '>', '/', '?'}   };
    int n = 4;
    int m = 24;
    double t_x, t_y, l_x, l_y = -1;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (kb_arr[i][j] == letter) {
                t_y = (double) i;
                t_x = (double) j;
            }
            if (kb_arr[i][j] == target) {
                l_y = (double) i;
                l_x = (double) j;
            }
        }
    }
    if (t_x == -1 || t_y == -1 || l_x == -1 || l_y == -1)
        return -1;

    double euc_x = abs(t_x - l_x) * abs(t_x - l_x);
    double euc_y = abs(t_y - l_y) * abs(t_y - l_y);
    double euc_dist = sqrt(euc_x + euc_y);
    return euc_dist;
}
