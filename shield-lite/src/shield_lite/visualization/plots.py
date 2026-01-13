def plot_dose_vs_t(mu_value, S, t_grid_mm, outpath):
    import matplotlib.pyplot as plt

    doses = [dose(thicknesses={'material': t}, mu={'material': mu_value}, S=S) for t in t_grid_mm]
    
    plt.figure()
    plt.plot(t_grid_mm, doses, label='Dose vs Thickness')
    plt.xlabel('Thickness (mm)')
    plt.ylabel('Dose (Gy)')
    plt.title('Dose vs Shield Thickness')
    plt.legend()
    plt.grid()
    plt.savefig(outpath)
    plt.close()

def plot_residuals(y, y_hat, outpath):
    import matplotlib.pyplot as plt

    residuals = y - y_hat
    
    plt.figure()
    plt.scatter(y_hat, residuals)
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel('Predicted Values')
    plt.ylabel('Residuals')
    plt.title('Residuals Plot')
    plt.grid()
    plt.savefig(outpath)
    plt.close()

def plot_pareto(pareto_points, outpath):
    import matplotlib.pyplot as plt

    plt.figure()
    plt.scatter(pareto_points['mass'], pareto_points['dose'], c='blue')
    plt.xlabel('Mass (kg)')
    plt.ylabel('Dose (Gy)')
    plt.title('Pareto Frontier')
    plt.grid()
    plt.savefig(outpath)
    plt.close()