# ---------------------------------------------------------------- #

import tensorflow as tf

from tf_agents.specs import tensor_spec

# ---------------------------------------------------------------- #

def get_num_obs_n_act(dataset_spec, obs_act):
    A = obs_act
    B = dataset_spec.has_log_probability()
    if not A and not B:
        raise ValueError(
            "Dataset must contain log-probability when obs_act is False.")

    spec_obs = dataset_spec.observation
    spec_act = dataset_spec.action

    if not is_categorical_spec(spec_obs):
        raise ValueError('Observation spec must be discrete and bounded.')

    if not is_categorical_spec(spec_act):
        raise ValueError('Action spec must be discrete and bounded.')

    num_obs = spec_obs.maximum + 1
    n_act = spec_act.maximum + 1

    return num_obs, n_act

def get_dim(num_obs, n_act, obs_act):
    x = num_obs * n_act
    y = num_obs
    A = obs_act
    dim = x if A else y

    return dim

def get_dims(dataset_spec, obs_act):
    num_obs, n_act = get_num_obs_n_act(dataset_spec, obs_act)
    dim = get_dim(num_obs, n_act, obs_act)

    return num_obs, n_act, dim


def is_categorical_spec(spec):
    A = tensor_spec.is_discrete(spec)
    B = tensor_spec.is_bounded(spec)
    C = spec.shape == []
    D = spec.minimum == 0

    return A and B and C and D

# -------------------------------- #

def obs_act_to_index(
        obs, act=None,
        num_obs=None, n_act=None,
        obs_act=True, neighbours="act"):

    o = tf.cast(obs, dtype=tf.int64)

    if not obs_act:
        return o

    else:
        a = tf.cast(act, dtype=tf.int64)

        if neighbours == "act":
            n_a = tf.cast(n_act, dtype=tf.int64)
            return o * n_a + a # type: ignore

        if neighbours == "obs":
            n_o = tf.cast(num_obs, dtype=tf.int64)
            return o + n_o * a # type: ignore

        raise ValueError


def index_to_obs_act(
        index,
        num_obs=None, n_act=None,
        obs_act=True, neighbours="act"):

    if not obs_act:
        return index

    else:
        n_a = tf.cast(n_act, dtype=tf.int64)
        n_o = tf.cast(num_obs, dtype=tf.int64)

        if neighbours == "act": return index // n_a, index %  n_a
        if neighbours == "obs": return index %  n_o, index // n_o
        raise ValueError

# ---------------------------------------------------------------- #