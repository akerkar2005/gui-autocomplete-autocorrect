#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <tuple>
#include <cmath>
#include <iostream>


using namespace std;

constexpr int ROWS = 4;
constexpr int COLS = 24;

char keyboard[ROWS][COLS] = {
    {'1', '!', '2', '@', '3', '#', '4', '$', '5', '%', '6', '^', '7', '&', '8', '*', '9', '(', '0', ')', '-', '_', '='},
    {'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '{', '[', '}', ']', '\\', '|'},
    {'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', ':', '"', '\''},
    {'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '<', '.', '>', '/', '?'}
};

struct Position {
    int x;
    int y;
};

Position get_position(char ch) {
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            if (keyboard[i][j] == ch)
                return {j, i};
        }
    }
    return {-1, -1};
}


double minDistance(const string &word1, const string &word2) {
  int m = word1.size();
  int n = word2.size();

  vector<vector<double>> cache(m + 1, vector<double>(n + 1)); 

  for (int j = 0; j <= n; j++) {
    cache[0][j] = static_cast<double>(j);
  }

  for (int i = 0; i <= m; i++) {
    cache[i][0] =  static_cast<double>(i);
  }

  // Compute the minimum distance
  for (int i = 1; i <= m; i++) {
    for (int j = 1; j <= n; j++) {
      if (word1[i - 1] == word2[j - 1]) {
        cache[i][j] = cache[i - 1][j - 1];  // No operation needed
      } else {
        cache[i][j] = min({1.0 + cache[i - 1][j], 1.0 + cache[i][j - 1], 1.0 + cache[i - 1][j - 1]});  // Take the minimum of insert, delete, replace
      }
    }
  }

  return cache[m][n];  // Return the minimum edit distance
}

double keyboardDist(const string &word1, const string &word2) {
    double dist = 0.0;
    size_t i = 0;
    size_t j = 0;

    while (i < word1.size() && j < word2.size()) {
        Position p1 = get_position(word1[i]);
        Position p2 = get_position(word2[j]);
        if (p1.x == -1 || p2.x == -1) {
          i++;
          j++;
          continue;
        }
        
        dist += sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2));
        i++;
        j++;
    }

    dist += 2.0 * fabs(static_cast<double>(word2.size()) - static_cast<double>(word1.size()));

    return dist;
}

vector<tuple<string, double, double>> compareWords(const string& input_word, const vector<string>& words) {
    vector<tuple<string, double, double>> res;

    for (const auto& word : words) {
        double edit_score = minDistance(input_word, word);
        double kb_score = keyboardDist(input_word, word);
        res.push_back(make_tuple(word, edit_score, kb_score));
    }

    return res;
}


PYBIND11_MODULE(MinDist, m) {
    m.def("compareWords", &compareWords, "A function that returns the resulting edit and keyboard distances of an array of words given an input word.",
                  pybind11::arg("input_word"), pybind11::arg("words"));
}
