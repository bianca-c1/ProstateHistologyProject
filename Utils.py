import numpy as np

class Utils:

    @staticmethod
    def tile(top_left, l, n):
        top = np.stack([np.linspace(top_left[0], top_left[0] + l, n // 4 + 1), np.full(n // 4 + 1, top_left[1])], axis=1)[
              :-1]
        left = np.stack([np.full(n // 4 + 1, top_left[0]), np.linspace(top_left[1], top_left[1] - l, n // 4 + 1)], axis=1)[
               :-1]

        right = left.copy()
        right[:, 0] += l
        bottom = top.copy()
        bottom[:, 1] -= l
        return np.concatenate([top, right, bottom, left])