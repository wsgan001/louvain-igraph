#ifndef GRAPHHELPER_INCLUDED
#define GRAPHHELPER_INCLUDED

#include <igraph.h>
#include <vector>
#include <exception>
#include <gsl_rng.h>
#include <gsl_randist.h>

#ifdef DEBUG
#include <iostream>
  using std::cerr;
  using std::endl;
#endif

class MutableVertexPartition;

using std::vector;
using std::pair;
using std::make_pair;

vector<size_t> range(size_t n);

bool pairCompareReverseSecond(const std::pair<size_t, size_t>& A, const std::pair<size_t, size_t>& B);

double KL(double q, double p);
double KLL(double q, double p);

template <class T> T sum(vector<T> vec)
{
  T sum_of_elems = T();
  for(typename vector<T>::iterator it=vec.begin();
      it!=vec.end();
      it++)
      sum_of_elems += *it;
  return sum_of_elems;
};

class Exception : std::exception
{
  public:
    Exception(const char* str)
    {
      this->str = str;
    }

    virtual const char* what() const throw()
    {
      return this->str;
    }

  private:
    const char* str;

};

class Graph
{
  public:
    Graph(igraph_t* graph,
      vector<double> edge_weights,
      vector<size_t> node_sizes,
      vector<double> node_self_weights, int correct_self_loops);
    Graph(igraph_t* graph,
      vector<double> edge_weights,
      vector<size_t> node_sizes,
      vector<double> node_self_weights);
    Graph(igraph_t* graph,
      vector<double> edge_weights,
      vector<size_t> node_sizes, int correct_self_loops);
    Graph(igraph_t* graph,
      vector<double> edge_weights,
      vector<size_t> node_sizes);
    Graph(igraph_t* graph, vector<double> edge_weights, int correct_self_loops);
    Graph(igraph_t* graph, vector<double> edge_weights);
    Graph(igraph_t* graph, int correct_self_loops);
    Graph(igraph_t* graph);
    Graph();
    ~Graph();

    int has_self_loops();
    size_t possible_edges();
    size_t possible_edges(size_t n);

    Graph* collapse_graph(MutableVertexPartition* partition);

    double weight_tofrom_community(size_t v, size_t comm, vector<size_t>* membership, igraph_neimode_t mode);
    vector< pair<size_t, size_t> >*
      get_neighbour_edges(size_t v, igraph_neimode_t mode);
    vector< size_t >*
      get_neighbours(size_t v, igraph_neimode_t mode);
    size_t get_random_neighbour(size_t v, igraph_neimode_t mode);
    size_t get_weighted_random_neighbour(size_t v, igraph_neimode_t mode);

    inline size_t get_random_node()
    {
      return this->get_random_int(0, this->vcount() - 1);
    };

    inline size_t get_random_int(size_t from, size_t to)
    {
      return igraph_rng_get_integer(igraph_rng_default(), from, to);
    };

    inline igraph_t* get_igraph() { return this->_graph; };

    inline size_t vcount() { return igraph_vcount(this->_graph); };
    inline size_t ecount() { return igraph_ecount(this->_graph); };
    inline double total_weight() { return this->_total_weight; };
    inline size_t total_size() { return this->_total_size; };
    inline int is_directed() { return igraph_is_directed(this->_graph); };
    inline double density() { return this->_density; };
    inline int correct_self_loops() { return this->_correct_self_loops; };
    inline int is_weighted() { return this->_is_weighted; };

    // Get weight of edge based on attribute (or 1.0 if there is none).
    inline double edge_weight(size_t e)
    {
      #ifdef DEBUG
      if (e > this->_edge_weights.size())
        throw Exception("Edges outside of range of edge weights.");
      #endif
      return this->_edge_weights[e];
    };

    inline vector<size_t> edge(size_t e)
    {
      igraph_integer_t v1, v2;
      igraph_edge(this->_graph, e, &v1, &v2);
      vector<size_t> edge(2);
      edge[0] = v1; edge[1] = v2;
      return edge;
    }

    // Get size of node based on attribute (or 1.0 if there is none).
    inline size_t node_size(size_t v)
    { return this->_node_sizes[v]; };

    // Get self weight of node based on attribute (or set to 0.0 if there is none)
    inline double node_self_weight(size_t v)
    { return this->_node_self_weights[v]; };

    inline size_t degree(size_t v, igraph_neimode_t mode)
    {
      if (mode == IGRAPH_IN)
        return this->_degree_in[v];
      else if (mode == IGRAPH_OUT)
        return this->_degree_out[v];
      else if (mode == IGRAPH_ALL)
        return this->_degree_all[v];
      else
        throw Exception("Incorrect mode specified.");
    };

    inline double strength(size_t v, igraph_neimode_t mode)
    {
      if (mode == IGRAPH_IN)
        return this->_strength_in[v];
      else if (mode == IGRAPH_OUT)
        return this->_strength_out[v];
      else
        throw Exception("Incorrect mode specified.");
    };

  protected:

    int _remove_graph;

  private:
    igraph_t* _graph;

    // Utility variables to easily access the strength of each node
    vector<double> _strength_in;
    vector<double> _strength_out;

    vector<size_t> _degree_in;
    vector<size_t> _degree_out;
    vector<size_t> _degree_all;

    vector<double> _edge_weights; // Used for the weight of the edges.
    vector<size_t> _node_sizes; // Used for the size of the nodes.
    vector<double> _node_self_weights; // Used for the self weight of the nodes.

    double _total_weight;
    size_t _total_size;
    int _is_weighted;

    int _correct_self_loops;
    double _density;

    int _initialized_weighted_neigh_selection;
    gsl_rng* _rng;
    vector<gsl_ran_discrete_t*> _weighted_neigh_prob_preproc; // Used for sampling a random neighbour when using a weighted graph.

    void init_admin();
    void init_weighted_neigh_selection();
    void set_defaults();
    void set_default_edge_weight();
    void set_default_node_size();
    void set_self_weights();

};

// We need this ugly way to include the MutableVertexPartition
// to overcome a circular linkage problem.
#include "MutableVertexPartition.h"

#endif // GRAPHHELPER_INCLUDED
