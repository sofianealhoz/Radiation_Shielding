def fit_S(y: np.ndarray) -> dict:
    from scipy.optimize import curve_fit
    import numpy as np

    def model(x, a, b):
        return a * x + b

    x_data = np.arange(len(y))
    params, _ = curve_fit(model, x_data, y)
    return {'S': params[0], 'intercept': params[1]}


def fit_S_mu_eff(t: np.ndarray, y: np.ndarray) -> dict:
    from scipy.optimize import curve_fit
    import numpy as np

    def model(x, mu_eff):
        return np.exp(-mu_eff * x)

    params, _ = curve_fit(model, t, y)
    return {'mu_eff': params[0]}