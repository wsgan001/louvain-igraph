import igraph as _ig
from . import _c_louvain
from .functions import _get_py_capsule
import sys
# Check if working with Python 3
PY3 = (sys.version > '3');

from .functions import ALL_COMMS
from .functions import ALL_NEIGH_COMMS
from .functions import RAND_COMM
from .functions import RAND_NEIGH_COMM

class Optimiser:
  """ Class for doing community detection using the Louvain algorithm.

  Given a certain partition type is calls diff_move for trying to move a node
  to another community. It moves the node to the community that *maximises*
  this diff_move. If no further improvement is possible, the graph is
  aggregated (collapse_graph) and the method is reiterated on that graph."""

  def __init__(self, eps=1e-5, delta=1e-2, max_itr=10000,
               random_order=True, consider_comms=ALL_NEIGH_COMMS):
    """ Create a new Optimiser object

    Parameters:
      eps=1e-5     -- If the improvement falls below this threshold,
                      stop iterating.
      delta=1e-2   -- If the number of nodes that moves falls below
                      this threshold, stop iterating.
      max_itr=1000 -- Maximum number of iterations to perform.
      random_order=True
                   -- If True the nodes will be traversed in a random order
                      when optimising a quality function.
      consider_comms=ALL_NEIGH_COMMS
                   -- This setting changes the way the communities are
                      considered for moving a node."""
    self._eps = eps;
    self._delta = delta;
    self._max_itr = max_itr;
    self._random_order = random_order;
    self._consider_comms = consider_comms;
    self._optimiser = _c_louvain._new_Optimiser(eps, delta, max_itr, random_order, consider_comms);

  #########################################################3
  # eps
  @property
  def eps(self):
    return self._eps;

  @eps.setter
  def eps(self, value):
    self._eps = value;
    _c_louvain._Optimiser_set_eps(self._optimiser, self._eps);

  #########################################################3
  # delta
  @property
  def delta(self):
    return self._delta;

  @delta.setter
  def delta(self, value):
    self._delta = value;
    _c_louvain._Optimiser_set_delta(self._optimiser, self._delta);

  #########################################################
  # max_itr
  @property
  def max_itr(self):
    return self._max_itr;

  @max_itr.setter
  def max_itr(self, value):
    self._max_itr = value;
    _c_louvain._Optimiser_set_max_itr(self._optimiser, self._max_itr);

  #########################################################3
  # random_order
  @property
  def random_order(self):
    return self._random_order;

  @random_order.setter
  def random_order(self, value):
    self._random_order = value;
    _c_louvain._Optimiser_set_random_order(self._optimiser, self._random_order);

  #########################################################3
  # consider_comms
  @property
  def consider_comms(self):
    return self._consider_comms;

  @consider_comms.setter
  def consider_comms(self, value):
    self._consider_comms = value;
    _c_louvain._Optimiser_set_consider_comms(self._optimiser, self._consider_comms);

  #########################################################3
  # move_individual
  @property
  def move_individual(self):
    return self._move_individual;

  @consider_comms.setter
  def move_individual(self, value):
    self._move_individual = value;
    _c_louvain._Optimiser_set_move_individual(self._optimiser, self._move_individual);

  #########################################################3
  # consider_empty_community
  @property
  def consider_empty_community(self):
    return self._consider_empty_community;

  @consider_comms.setter
  def consider_empty_community(self, value):
    self._consider_empty_community = value;
    _c_louvain._Optimiser_set_consider_empty_community(self._optimiser, self._consider_empty_community);

  #########################################################3
  # smart_local_move
  @property
  def smart_local_move(self):
    return self._smart_local_move;

  @smart_local_move.setter
  def smart_local_move(self, value):
    self._smart_local_move = value;
    _c_louvain._Optimiser_set_smart_local_move(self._optimiser, self._smart_local_move);

  #########################################################3
  # aggregate_smart_local_move
  @property
  def aggregate_smart_local_move(self):
    return self._aggregate_smart_local_move;

  @consider_comms.setter
  def aggregate_smart_local_move(self, value):
    self._aggregate_smart_local_move = value;
    _c_louvain._Optimiser_set_aggregate_smart_local_move(self._optimiser, self._aggregate_smart_local_move);

  def optimize_partition(self, partition):
    """ Find optimal partition given the specific type of partition_class that
    is provided.

    Parameters:
      partition       -- The partition to optimize"""
    # Perhaps we
    diff = _c_louvain._Optimiser_optimize_partition(self._optimiser, partition._partition);
    partition._update_internal_membership();
    return diff;

  def optimize_partition_multiplex(self, partitions, layer_weights=None):
    """
      Method for detecting communities using the Louvain algorithm. This functions
      finds the optimal partition for all layers given the specified methods. For
      the various possible methods see package documentation. This considers all
      graphs in all layers, in which each node may be differently connected, but all
      nodes must appear in all graphs. Furthermore, they should have identical
      indices in the graph (i.e. node i is assumed to be the same node in all
      graphs).  The quality of this partition is simply the sum of the individual
      qualities for the various partitions, weighted by the layer_weight. If we
      denote by q_k the quality of layer k and the weight by w_k, the overall
      quality is then
      q = sum_k w_k*q_k.

      Notice that this is particularly useful for graphs containing negative links.
      When separating the graph in two graphs, the one containing only the positive
      links, and the other only the negative link, by supplying a negative weight to
      the latter layer, we try to find relatively many positive links within a
      community and relatively many negative links between communities.
      """
    if not layer_weights:
      layer_weights = [1]*len(partitions);
    diff = _c_louvain._Optimiser_optimize_partition_multiplex(
      self._optimiser,
      [partition._partition for partition in partitions],
      layer_weights);
    for partition in partitions:
      partition._update_internal_membership();
    return diff;

  def move_nodes(self, partition):
    """ Move nodes to neighbouring communities such that each move improves the
    given quality function maximally (i.e. greedily).

    Parameters:
      partition -- The partition to optimise.
    """
    diff =  _c_louvain._Optimiser_move_nodes(self._optimiser, partition._partition);
    partition._update_internal_membership();
    return diff;

  def bisect(
        graph,
        method,
        resolution_range,
        weight=None,
        consider_comms=ALL_NEIGH_COMMS,
        bisect_func=lambda p: p.total_weight_in_all_comms(),
        min_diff_bisect_value=1,
        min_diff_resolution=1e-3,
        linear_bisection=False,
        ):
    """ Use bisectioning on the resolution parameter in order to construct a
    resolution profile.

    Keyword arguments:

    graph
      The graph for which to find the optimal partition(s).

    method
      The method used to find a partition (must support resolution parameters
      obviously).

    resolution_range
      The range of resolution values that we would like to scan.

    weight=None
      If provided, indicates the edge attribute to use as a weight.

    consider_comms=ALL_NEIGH_COMMS
      This parameter determines which communities to consider when moving a node.
      Please refer to the documentation of `find_partition` for more information
      on this parameter.

    bisect_func=total_internal_edges
      The function used for bisectioning. For the methods currently implemented,
      this should usually not be altered.

    min_diff_bisect_value=1
      The difference in the value returned by the bisect_func below which the
      bisectioning stops (i.e. by default, a difference of a single edge does not
      trigger further bisectioning).

    min_diff_resolution=1e-3
      The difference in resolution below which the bisectioning stops. For
      positive differences, the logarithmic difference is used by default, i.e.
      ``diff = log(res_1) - log(res_2) = log(res_1/res_2)``, for which ``diff >
      min_diff_resolution`` to continue bisectioning. Set the linear_bisection to
      true in order to use only linear bisectioning (in the case of negative
      resolution parameters for example, which can happen with negative weights).

    linear_bisection=False
      Whether the bisectioning will be done on a linear or on a logarithmic basis
      (if possible).

    returns: a list of partitions and resolution values.
      """
    # Helper function for cleaning values to be a stepwise function
    def clean_stepwise(bisect_values):
      # We only need to keep the changes in the bisection values
      bisect_list = sorted([(res, part.bisect_value) for res, part in
        bisect_values.iteritems()], key=lambda x: x[0]);
      for (res1, v1), (res2, v2) \
          in zip(bisect_list,
                 bisect_list[1:]):
        # If two consecutive bisection values are the same, remove the second
        # resolution parameter
        if v1 == v2:
          del bisect_values[res2];
    # We assume here that the bisection values are
    # monotonically decreasing with increasing resolution
    # parameter values
    def ensure_monotonicity(bisect_values, new_res):
      for res, bisect_part in bisect_values.iteritems():
        # If at a lower resolution value there were lower bisection values, we
        # should update them in order to maintain monotonicity
        if res < new_res and \
           bisect_part.bisect_value < bisect_values[new_res].bisect_value:
          bisect_values[res] = bisect_values[new_res];
        # If at a higher resolution value there were higher bisection values, we
        # should update them in order to maintain monotonicity
        elif res > new_res and \
           bisect_part.bisect_value > bisect_values[new_res].bisect_value:
          bisect_values[res] = bisect_values[new_res];
    # Start actual bisectioning
    bisect_values = {};
    stack_res_range = [];
    # Push first range onto the stack
    stack_res_range.append(resolution_range);
    # Make sure the bisection values are calculated
    # The namedtuple we will use in the bisection function
    BisectPartition = namedtuple('BisectPartition',
        ['partition', 'bisect_value']);
    partition = find_partition(graph=graph, method=method, weight=weight,
                                   resolution_parameter=resolution_range[0], consider_comms=consider_comms);
    bisect_values[resolution_range[0]] = BisectPartition(partition=partition,
                                bisect_value=bisect_func(partition));
    partition = find_partition(graph=graph, method=method, weight=weight,
                                   resolution_parameter=resolution_range[1], consider_comms=consider_comms);
    bisect_values[resolution_range[1]] = BisectPartition(partition=partition,
                                bisect_value=bisect_func(partition));
    # While stack of ranges not yet empty
    while stack_res_range:
      # Get the current range from the stack
      current_range = stack_res_range.pop();
      # Get the difference in bisection values
      diff_bisect_value = abs(bisect_values[current_range[0]].bisect_value -
                              bisect_values[current_range[1]].bisect_value);
      # Get the difference in resolution parameter (in log space if 0 is not in
      # the interval (assuming only non-negative resolution parameters).
      if current_range[0] > 0 and current_range[1] > 0 and not linear_bisection:
        diff_resolution = log(current_range[1]/current_range[0]);
      else:
        diff_resolution = abs(current_range[1] - current_range[0]);
      # Check if we still want to scan a smaller interval
      logging.info('Range=[{0}, {1}], diff_res={2}, diff_bisect={3}'.format(
          current_range[0], current_range[1], diff_resolution, diff_bisect_value));
      # If we would like to bisect this interval
      if diff_bisect_value > min_diff_bisect_value and \
         diff_resolution > min_diff_resolution:
        # Determine new resolution value
        if current_range[0] > 0 and current_range[1] > 0 and not linear_bisection:
          new_res = sqrt(current_range[1]*current_range[0]);
        else:
          new_res = sum(current_range)/2.0;
        # Bisect left (push on stack)
        stack_res_range.append((current_range[0], new_res));
        # Bisect right (push on stack)
        stack_res_range.append((new_res, current_range[1]));
        # If we haven't scanned this resolution value yet,
        # do so now
        if not bisect_values.has_key(new_res):
          partition = find_partition(graph, method=method, weight=weight,
                                         resolution_parameter=new_res, consider_comms=consider_comms);
          bisect_values[new_res] = BisectPartition(partition=partition,
                                      bisect_value=bisect_func(partition));
          logging.info('Resolution={0}, Resolution Value={1}'.format(new_res,
            bisect_func(partition)));
        # Because of stochastic differences in different runs, the monotonicity
        # of the bisection values might be violated, so check for any
        # inconsistencies
        ensure_monotonicity(bisect_values, new_res);
    # Ensure we only keep those resolution values for which
    # the bisection values actually changed, instead of all of them
    clean_stepwise(bisect_values);
    # Use an ordered dict so that when iterating over it, the results appear in
    # increasing order based on the resolution value.
    return OrderedDict(sorted(((res, part) for res, part in
      bisect_values.iteritems()), key=lambda x: x[0]));