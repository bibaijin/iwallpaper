import numpy as np

import iwallpaper.ai as ai
from iwallpaper.config import CONFIG


def test_rank_to_y():
    assert np.equal(ai.Rank(1).to_y(), [1, 0, 0, 0, 0]).all()
    assert np.equal(ai.Rank(2).to_y(), [0, 1, 0, 0, 0]).all()
    assert np.equal(ai.Rank(3).to_y(), [0, 0, 1, 0, 0]).all()
    assert np.equal(ai.Rank(4).to_y(), [0, 0, 0, 1, 0]).all()
    assert np.equal(ai.Rank(5).to_y(), [0, 0, 0, 0, 1]).all()


def test_network_init_theta():
    init_theta = ai.NETWORK.init_theta()
    assert init_theta.shape == ((CONFIG.a1_number + 1) * CONFIG.a2_number +
                                (CONFIG.a2_number + 1) * CONFIG.a3_number, )


def test_network_merge_matrix():
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])
    assert np.equal(ai.NETWORK.merge_matrix(A, B),
                    [1, 2, 3, 4, 5, 6, 7, 8]).all()


def test_network_separate_theta():
    theta = ai.NETWORK.init_theta()
    Theta1, Theta2 = ai.NETWORK.separate_theta(theta)
    assert Theta1.shape == (CONFIG.a1_number + 1, CONFIG.a2_number)
    assert Theta2.shape == (CONFIG.a2_number + 1, CONFIG.a3_number)
    assert np.equal(ai.NETWORK.merge_matrix(Theta1, Theta2), theta).all()


def test_network_init_epsilon():
    assert ai.NETWORK.init_epsilon(3, 3) == 1


def test_network_J():
    Theta1 = np.array([[0, 0], [1, 0], [0, 1]])
    Theta2 = np.array([[0, 0], [1, 0], [0, 1]])
    x = np.array([0, 0])
    y = np.array([1, 0])
    lambda_ = 1

    # z2 = np.array([0, 0])
    # a2 = np.array([0.5, 0.5])
    # z3 = np.array([0.5, 0.5])
    # a3 = np.array([0.62, 0.62])
    expect_cost = 0.48 + 0.97
    expect_cost += 0.5 * (2 + 2)

    got_cost, _, _ = ai.NETWORK.J_and_gradient(Theta1, Theta2, x, y, lambda_)

    assert (got_cost - expect_cost) < 0.1


def test_network_gradient():
    x = np.random.random(CONFIG.a1_number)
    y = np.array([1, 0, 0, 0, 0])
    lambda_ = 1
    Theta1, Theta2 = ai.NETWORK.separate_theta(ai.NETWORK.init_theta())
    Theta1[1, 0] += 0.0001
    J1, got_D1_1, _ = ai.NETWORK.J_and_gradient(Theta1, Theta2, x, y, lambda_)
    Theta1[1, 0] -= 0.0002
    J2, got_D1_2, _ = ai.NETWORK.J_and_gradient(Theta1, Theta2, x, y, lambda_)
    assert (got_D1_1[1, 0] - got_D1_2[1, 0]) < 0.1
    expect_D1 = (J1 - J2) / 0.0002
    assert (got_D1_1[1, 0] - expect_D1) < 0.01
