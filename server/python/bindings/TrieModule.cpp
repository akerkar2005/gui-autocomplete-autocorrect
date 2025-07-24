#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <iostream>

using namespace std;
namespace py = pybind11;

template <typename K, typename V>

/* To compile this module, use: g++ -O3 -Wall -shared -std=c++17 -fPIC $(python3 -m pybind11 --includes) TrieModule.cpp -o TrieModule.dylib */

class HashTable {
private:

    struct Entry {
        K key;
        V value;
        bool deleted;
        bool vacant;

        Entry() : key(), value(), deleted(false), vacant(true) {}
        Entry(K key, V value) : key(key), value(value), deleted(false), vacant(false) {}
    };

    Entry* table;
    int capacity;
    int num_elements;
    const int DEFAULT_CAPACITY = (1 << 4) + 3;
    const double LOAD_FACTOR = 0.75;
    const int CAPACITY_INCREMENT = 1 << 5;
    vector<pair<K, V>> valid_elements;

    int hash(const K key) const {
    #define ABS(x) ((x < 0) ? (-x) : (x))
        return ABS(std::hash<K>{}(key) % capacity);
    }

    int hashFunc(int h, int i) const {
        const int idx = (h + i * i) % capacity;
        return idx;
    }

    void resize() {
        //int old_capacity = capacity;
        int new_capacity;
        try {
            if (capacity > INT_MAX / 2) {
                throw std::overflow_error("Doubling capacity causes overflow.");
            }
            new_capacity = capacity * 2;
        } catch (const std::overflow_error&) {
            if (capacity > INT_MAX - CAPACITY_INCREMENT) {
                throw std::overflow_error("Cannot increase capacity without overflow.");
            }
            new_capacity = capacity + CAPACITY_INCREMENT;
        }
        
        // Create a new table with the new capacity
        Entry* new_table = new Entry[new_capacity]();

        // Rehash all entries into the new table
        for (int i = 0; i < capacity; i++) {

            // only add entries from the old table to the new table that are not vacant
            // or deleted.

            if (!table[i].vacant && !table[i].deleted) {
                int h = std::hash<K>{}(table[i].key) % new_capacity;
                for (int j = 0; j < new_capacity; j++) {
                    int idx = (h + j * j) % new_capacity;
                    if (new_table[idx].vacant) {
                        new_table[idx] = Entry(table[idx].key, table[idx].value);
                        break;
                    }
                }
            }
        }

        delete[] table;
        table = new_table;
        capacity = new_capacity;
    }

public:

    /*
     * Hash Table with Quadratic Probing
     */ 
    HashTable(int init_capacity) : num_elements(0) {
        if (init_capacity <= 0 || init_capacity > INT_MAX) {
            std::cout << init_capacity << std::endl;
            throw std::invalid_argument("Invalid Capacity");
        }
        capacity = DEFAULT_CAPACITY < init_capacity ? init_capacity : DEFAULT_CAPACITY;
        table = new Entry[capacity]();
    }

    HashTable() : capacity(DEFAULT_CAPACITY), num_elements(0) {
        table = new Entry[capacity]();
    }

    ~HashTable() {
        delete[] table;
    }

    void insert(const K key, const V value) {
        if constexpr (std::is_pointer<K>::value && std::is_pointer<V>::value) {
            if (key == nullptr) throw std::runtime_error("Inserting a null key or value is disallowed.");
        }
        double load = (double) (num_elements + 1) / (double) capacity;
        if (load > LOAD_FACTOR) {   
            resize();
        }

        pair<K, V> new_pair;
        new_pair.first = key;
        new_pair.second = value;
        valid_elements.push_back(new_pair);

        int h = hash(key);

        for (int i = 0; i < capacity; i++) {
            int idx = hashFunc(h, i);

            if (table[idx].vacant || table[idx].deleted) {
                /* create a new entry when finding an empty spot */
                table[idx] = Entry(key, value);
                num_elements++;
                return;
            }

            if (table[idx].key == key) {
                /* update an old entry's value to the value passed in when finding the same key */
                table[idx].value = value;
                return;
            }
        }
    }

    void remove(K key) {
        if constexpr (std::is_pointer<K>::value) {
            if (key == nullptr) throw std::runtime_error("Tried to remove a null key; this is disallowed.");
        }
        if (num_elements == 0) return;

        for(int i = 0; i < capacity; i++) {
            int idx = hashFunc(hash(key), i);

            /* If we come across a vacant entry, this means that */
            /* the key we are trying to remove does not exist and we */
            /* may stop probing. If we come across a DELETED entry, */
            /* we can conclude that we MUST keep probing since the */
            /* entry we are looking for may exist later on in the table. */

            if (table[idx].vacant) return;
            if (table[idx].deleted) continue;
            
            /* If we find the value with no issues, we may delete it. */
            if (table[idx].key == key) {
                table[idx].key = K();
                table[idx].value = V();
                table[idx].deleted = true;
                num_elements--;
                //for (int i = 0; i < valid_elements.size(); i++) {
                //    if (valid_elements[i].first == key) {
                //        vector.erase(vector.begin() + i);
                //        break;
                //    }
                //}
                return;
            }
        }
    }

    V get(const K key) {
        if constexpr (std::is_pointer<K>::value) {
            if (key == nullptr) throw std::out_of_range("key is not valid.");
        }

        if (this->num_elements == 0) throw std::out_of_range("key is not valid.");

        for (int i = 0; i < capacity; i++) {
            int idx = hashFunc(hash(key), i);

            /* Similar to the remove function, if we encounter a vacant entry, */
            /* we may stop probing and conclude that the entry does not exist. */
            /* If we encounter a DELETED entry, we MUST continue probing because */
            /* there is a chance the entry does exist. */

            if (table[idx].vacant) throw std::out_of_range("key is not valid.");
            if (table[idx].deleted) continue;

            /* If we successfully found the value, we may return it. */
            if (table[idx].key == key) return table[idx].value;
        }
        throw out_of_range("key is not valid.");
    }

    vector<pair<K, V>> getValidTableValues() {
        return valid_elements;
    }


    bool containsKey(const K key) {
        if constexpr (std::is_pointer<K>::value) {
            if (key == nullptr) throw std::out_of_range("key is not valid.");
        } 
        if (num_elements == 0) return false;
        for (int i = 0; i < capacity; i++) {
            int idx = hashFunc(hash(key), i);

            /* same logic as get and remove. */ 
            /* vacant = stop probing and return false. */
            /* deleted = continue probing. */

            if (table[idx].vacant) return false;
            if (table[idx].deleted) continue;
            if (table[idx].key == key) return true;
        }
        return false;
    }

    int size() const { return num_elements; }
};

class Trie {

private:

    struct Node {
        HashTable<char, Node*> children;
        bool isEndOfWord;
        
        Node() : children(50), isEndOfWord(false) {}

    };

    Node* root;

    void dfs(Node *node, const string& prefix, vector<string>& words) const {
        if (node->isEndOfWord) {
            if (words.size() < 3) {
                int flag = 1;
                for (size_t i = 0; i < words.size(); i++) {
                    if (words[i] == prefix)
                        flag = 0;
                }
                if (flag)
                    words.push_back(prefix);
            }
            else {
                for (int i = 0; i < 3; i++) {
                    if (words[i] == prefix)
                      continue;
                    if (words[i].length() > prefix.length())
                        words[i] = prefix;
                }
            }
        }
        vector<pair<char, Node*>> table = node->children.getValidTableValues();
        for (const pair<char, Node*> &neighbor: table) {
            dfs(neighbor.second, prefix + neighbor.first, words);
        }
    }

    void deleteTrie(Node *node) {
      if (!node)
        return;

      vector<pair<char, Node*>> table = node->children.getValidTableValues();

      for (const pair<char, Node*> &neighbor: table) {
          deleteTrie(neighbor.second);
      }

      delete node;
    }

public:

    Trie() {
        root = new Node;
    }

    ~Trie() {
        deleteTrie(root);
    }

    /* inserting a word into the Trie */
    void insert(const string& word) {
        Node* current = root;
        for (char c : word) {
            try {
                current->children.get(c);
            }
            catch (const out_of_range& e) {
                Node* node = new Node();
                current->children.insert(c, node); 
            }
            current = current->children.get(c);
        }
        current->isEndOfWord = true;
    }

    vector<string> search(const string& prefix) const {
        Node* current = root;
        for (char c : prefix) {
            try {
                current->children.get(c);
            }
            catch (const out_of_range& e) {
                return {}; /* prefix was not found */
            }
            current = current->children.get(c);
        }
        vector<string> words;
        dfs(current, prefix, words);
        return words;
    }
};




PYBIND11_MODULE(TrieModule, m) {
    py::class_<Trie>(m, "Trie")
        .def(py::init<>())
        .def("insert", &Trie::insert)
        .def("search", &Trie::search);
}
