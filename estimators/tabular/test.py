# ---------------------------------------------------------------- #

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf

import os

from dice_rl_TU_Vienna.utils.numpy import safe_divide

# ---------------------------------------------------------------- #

def test_estimator(estimator_DICE, gamma, projected, weighted, **kwargs):

    # -------------------------------- #

    d0_bar, dD_bar, P_bar, r_bar, n = estimator_DICE.auxiliary_estimates.bar

    d0_hat = d0_bar / n
    dD_hat = dD_bar / n
    r_hat = safe_divide(r_bar, dD_bar)

    pv, sdc_hat, _ = estimator_DICE.solve(
        gamma, projected=projected, weighted=weighted, **kwargs)

    d_hat = sdc_hat * dD_hat

    pv = float(pv)
    print(f"{pv=}")
    print(f"{np.dot(sdc_hat, dD_hat)=}")
    print()

    # -------------------------------- #

    _, ax = plt.subplots(nrows=2, figsize=(12, 6), sharex=True)

    ax[0].bar(range(len(sdc_hat)), sdc_hat)
    ax[1].bar(range(len(d_hat)), d_hat)

    ax[0].set_ylabel(r"$\hat{w}_{\pi / D}(s, a)$")
    ax[1].set_ylabel(r"$\hat{d}^\pi      (s, a)$")

    str_gamma = r"\gamma"
    plt.suptitle(f"${str_gamma} = {gamma}$")
    plt.xlabel(r"$(s, a)$-index")

    plt.show()

    # -------------------------------- #


def test_auxiliary_estimates(auxiliary_estimates, title_prefix, dir=None, epsilon=1e-4):

    if dir is not None:
        if not tf.io.gfile.isdir(dir):
            tf.io.gfile.makedirs(dir)

    def get_path(file_name):
        assert dir is not None
        fn = title_prefix + "; " + f"{file_name}.png"
        path = os.path.join(dir, fn)
        return path

    color = "blue"
    alpha = 0.25

    # -------------------------------- #

    d0_bar, dD_bar, P_bar, r_bar, n = auxiliary_estimates.bar

    d0_hat = d0_bar / n
    dD_hat = dD_bar / n
    r_hat = safe_divide(r_bar, dD_bar)

    mask = dD_bar == 0

    d0_bar_mask = d0_bar[~mask]
    dD_bar_mask = dD_bar[~mask]
    P_bar_mask  = P_bar[~mask, :][:, ~mask]
    r_bar_mask  = r_bar[~mask]

    # -------------------------------- #

    print("# (s, a) visited:")
    a = np.sum(~mask); r = a / len(dD_bar)
    print({"absolute": a, "relative": r})

    print("# (s, a) not visited:")
    a = np.sum(mask); r = a / len(dD_bar)
    print({"absolute": a, "relative": r})

    print()
    x = np.sum(P_bar[mask, :] != 0)
    y = np.sum(P_bar[:, mask] != 0)
    s_x = r"#{i: dD_bar[i] == 0, P_bar[i, :] != 0} ="
    s_y = r"#{i: dD_bar[i] == 0, P_bar[:, i] != 0} ="
    print(s_x, x)
    print(s_y, y)
    z = np.sum(d0_bar[mask] != 0)
    s_z = r"#{i: dD_bar[i] == 0, d0_bar[i] != 0} ="
    print(s_z, z)

    print()
    print("#", "-"*64, "#", "\n")

    # -------------------------------- #

    _, ax = plt.subplots(nrows=3, figsize=(12, 9), sharex=True, tight_layout=True)

    ax[0].bar(range(len(d0_hat)), d0_hat, color=color, alpha=alpha)
    ax[1].bar(range(len(dD_hat)), dD_hat, color=color, alpha=alpha)
    ax[2].bar(range(len(r_hat)),  r_hat,  color=color, alpha=alpha)

    ax[0].set_ylabel(r"$\hat{d}_0(s, a)$")
    ax[1].set_ylabel(r"$\hat{d}^D(s, a)$")
    ax[2].set_ylabel(r"$\hat{r}  (s, a)$")

    for i in range( len(ax) ):
        ax[i].grid(linestyle=":")

    plt.xlabel(r"$(s, a)$-index")

    plt.suptitle(title_prefix)

    if dir is not None:
        file_name = "d0_hat, dD_hat, r_hat"
        path = get_path(file_name)
        plt.savefig(path, bbox_inches="tight")

    plt.show()

    # -------------------------------- #

    plt.plot()
    plt.imshow( pd.DataFrame(P_bar), cmap="Greys", vmin=0, vmax=1, )
    plt.colorbar()
    plt.xlabel(r"$(s, a)$-index")
    plt.ylabel(r"$(s, a)$-index")
    plt.suptitle(title_prefix + "; " + r"$\bar{P}^\pi$")
    if dir is not None:
        file_name = "P_bar"
        path = get_path(file_name)
        plt.savefig(path, bbox_inches="tight")
    plt.show()

    plt.plot()
    plt.imshow( pd.DataFrame(P_bar_mask), cmap="Greys", vmin=0, vmax=1, )
    plt.colorbar()
    plt.xlabel(r"masked $(s, a)$-index")
    plt.ylabel(r"masked $(s, a)$-index")
    plt.suptitle(title_prefix + "; " + r"$\bar{P}^{\pi, \text{mask}}$")
    if dir is not None:
        file_name = "P_bar_mask"
        path = get_path(file_name)
        plt.savefig(path, bbox_inches="tight")
    plt.show()

    print("#", "-"*64, "#", "\n")

    # -------------------------------- #

    def test_sum(bar, mask=False):

        d0_bar, dD_bar, P_bar, r_bar, n = bar

        d0_hat = d0_bar / n
        dD_hat = dD_bar / n
        P_hat = safe_divide(P_bar.T, dD_bar).T

        s_d0 = np.sum(d0_hat)
        s_dD = np.sum(dD_hat)
        s_P  = np.sum(P_hat, axis=1)

        a = np.sum(                       s_P <   -epsilon  )
        x = np.sum( (-epsilon  <= s_P) * (s_P <=   epsilon) )
        y = np.sum( (  epsilon <  s_P) * (s_P <  1-epsilon) )
        z = np.sum( (1-epsilon <= s_P) * (s_P <= 1+epsilon) )
        b = np.sum( (1+epsilon <  s_P)                      )
        values = [a, x, y, z, b]

        labels = [
            r"$\sigma_{(s, a)} < -\varepsilon$",
            r"$-\varepsilon \leq \sigma_{(s, a)} \leq \varepsilon$",
            r"$\varepsilon < \sigma_{(s, a)} < 1-\varepsilon$",
            r"$1-\varepsilon \leq \sigma_{(s, a)} \leq 1+\varepsilon$",
            r"$1+\varepsilon < \sigma_{(s, a)}$",
        ]

        plt.figure( figsize=(12, 4), )
        bar = plt.bar(labels, values, color=color, alpha=alpha)
        plt.bar_label(bar, label_type="center")
        space = r"S \times A" if not mask else r"(S \times A)^\text{mask}"
        matrix = r"\hat{P}^\pi" if not mask else r"\hat{P}^{\pi, \text{mask}}"
        x = r"\sigma_{(s, a)} = \sum_{(s^\prime, a^\prime) \in " + space + r"} " + matrix + r"_{(s, a), (s^\prime, a^\prime)}"
        y = r"\varepsilon = " + str(epsilon)
        plt.suptitle(title_prefix + "; " + f"${x}" + ", \quad " + f"{y}$", y=1.025)
        plt.ylabel(r"$\# \{ (s, a) \mid \dots \}$")
        distribution = r"\hat{d}_0^\pi" if not mask else r"\hat{d}_0^{\pi, \text{mask}}"
        x = r"\sum_{(s, a) \in S \times A} " + distribution + "(s, a) = " + str(s_d0)
        distribution = r"\hat{d}^D" if not mask else r"\hat{d}^D_{\text{mask}}"
        y = r"\sum_{(s, a) \in S \times A} " + distribution + "(s, a) = " + str(s_dD)
        plt.figtext(0.5, -0.025, f"${x}" + ", \quad " + f"{y}$", ha="center")

        if dir is not None:
            file_name = "sums"
            if mask: file_name += "_" + "mask"
            path = get_path(file_name)
            plt.savefig(path, bbox_inches="tight")

        plt.show()

    test_sum(
        bar=(d0_bar, dD_bar, P_bar, r_bar, n),
        mask=False,
    )

    test_sum(
        bar=(d0_bar_mask, dD_bar_mask, P_bar_mask, r_bar_mask, n),
        mask=True,
    )

    print("#", "-"*64, "#", "\n")

# ---------------------------------------------------------------- #
