# beta
from src.analysis.io.loader import DataLoader
from src.analysis.io.logger import log
from src.f031_rnn_modeling.analysis import simulate_predictive_rnn, analyze_rnn_prediction_errors
from src.f031_rnn_modeling.plot import plot_rnn_modeling

def run_f031():
    """
    Main execution entry for Figure 31.
    """
    log.progress("Starting Analysis f031: RNN Modeling")
    loader = DataLoader()
    output_dir = loader.get_output_dir("f031_rnn_modeling")
    
    h_std, h_omit = simulate_predictive_rnn()
    error = analyze_rnn_prediction_errors(h_std, h_omit)
    
    plot_rnn_modeling(h_std, h_omit, error, output_dir)
    log.progress("Analysis f031 complete.")

if __name__ == "__main__":
    run_f031()
