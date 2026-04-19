# beta
import numpy as np
import jax
import jax.numpy as jnp
from src.analysis.io.logger import log

def rnn_step(h, x, W_hh, W_xh, b_h):
    """Simple RNN transition step."""
    return jnp.tanh(jnp.dot(W_hh, h) + jnp.dot(W_xh, x) + b_h)

def simulate_predictive_rnn(seq_len=20, n_hidden=64, input_dim=1):
    """
    Simulates a simple RNN trained to predict a sequence (e.g. A-A-A-B).
    During the 'omission' trial, input is set to zero.
    """
    key = jax.random.PRNGKey(42)
    W_hh = jax.random.normal(key, (n_hidden, n_hidden)) * 0.1
    W_xh = jax.random.normal(key, (n_hidden, input_dim)) * 0.1
    b_h = jnp.zeros(n_hidden)
    
    # 1. Standard Input (A-A-A-B) - Pulse at t=0, 5, 10, 15
    inputs_std = jnp.zeros((seq_len, input_dim))
    inputs_std = inputs_std.at[0].set(1.0).at[5].set(1.0).at[10].set(1.0).at[15].set(2.0) # B is 2.0
    
    # 2. Omission Input (A-X-A-B)
    inputs_omit = jnp.zeros((seq_len, input_dim))
    inputs_omit = inputs_omit.at[0].set(1.0).at[5].set(0.0).at[10].set(1.0).at[15].set(2.0)
    
    def run_seq(inputs):
        h = jnp.zeros(n_hidden)
        hs = []
        for t in range(seq_len):
            h = rnn_step(h, inputs[t], W_hh, W_xh, b_h)
            hs.append(h)
        return jnp.array(hs)
        
    h_std = run_seq(inputs_std)
    h_omit = run_seq(inputs_omit)
    
    return h_std, h_omit

def analyze_rnn_prediction_errors(h_std, h_omit):
    """
    Computes a simple 'prediction error' metric as the Euclidean distance 
    between standard and omission hidden states.
    """
    error = jnp.linalg.norm(h_std - h_omit, axis=-1)
    return error
