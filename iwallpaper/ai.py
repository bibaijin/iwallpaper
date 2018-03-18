import cv2
import logging
import numpy as np
import os.path
from scipy.optimize import minimize

from iwallpaper.config import CONFIG
import iwallpaper.util as util


class Image:
    '''
    Image is input
    '''

    def __init__(self, filename):
        self.__filename = filename

    def to_x(self):
        img = cv2.imread(self.__filename)
        height, width, color_number = img.shape
        img = cv2.resize(img, (CONFIG.resized_width, CONFIG.resized_height))
        img = img.reshape(
            CONFIG.resized_height * CONFIG.resized_width * color_number)
        return np.r_[height / CONFIG.standard_height,
                     width / CONFIG.standard_width, img / 255]


class Rank:
    '''
    Rank is output
    '''

    def __init__(self, rank):
        self.__rank = rank

    def to_y(self):
        y = np.zeros((5))
        y[self.__rank - 1] = 1
        return y


class Network:
    '''
    Network is neural network
    '''

    def init_theta(self):
        if os.path.isfile(CONFIG.theta_file):
            return np.load(CONFIG.theta_file)

        e1 = self.init_epsilon(CONFIG.a1_number, CONFIG.a2_number)
        Theta1 = np.random.random(
            (CONFIG.a1_number + 1, CONFIG.a2_number)) * 2 * e1 - e1
        e2 = self.init_epsilon(CONFIG.a2_number, CONFIG.a3_number)
        Theta2 = np.random.random(
            (CONFIG.a2_number + 1, CONFIG.a3_number)) * 2 * e2 - e2
        return self.merge_matrix(Theta1, Theta2)

    def __save_theta(self, theta):
        np.save(CONFIG.theta_file, theta)

    def merge_matrix(self, A, B):
        return np.r_[A.reshape(A.size), B.reshape(B.size)]

    def separate_theta(self, theta):
        n1 = (CONFIG.a1_number + 1) * CONFIG.a2_number
        theta1 = theta[:n1]
        Theta1 = theta1.reshape((CONFIG.a1_number + 1, CONFIG.a2_number))
        theta2 = theta[n1:]
        Theta2 = theta2.reshape((CONFIG.a2_number + 1, CONFIG.a3_number))
        return Theta1, Theta2

    def init_epsilon(self, l_in, l_out):
        return (6**0.5) / ((l_in + l_out)**0.5)

    def __sigmoid(self, z):
        '''
        __sigmoid is the sigmoid function
        '''
        return 1 / (1 + np.exp(-z))

    def J_and_gradient(self, Theta1, Theta2, X, Y, lambda_):
        '''
        J is the cost function
        '''
        m, _ = X.shape
        z2 = np.dot(np.c_[np.ones((m, 1)), X], Theta1)
        a2 = self.__sigmoid(z2)
        z3 = np.dot(np.c_[np.ones((m, 1)), a2], Theta2)
        a3 = self.__sigmoid(z3)
        cost = (1 / m) * np.sum(-Y * np.log(a3) - (1 - Y) * np.log(1 - a3))
        cost += (lambda_ / 2) * (np.sum(Theta1[1:]**2) + np.sum(Theta2[1:]**2))

        D2 = np.zeros_like(Theta2)
        D1 = np.zeros_like(Theta1)
        for t in range(m):
            delta3 = a3[t, :] - Y[t, :]
            Delta2 = np.outer(np.r_[1, a2[t, :]], delta3)
            D2 += Delta2
            D2[1:, :] += lambda_ * Theta2[1:, :]
            delta2 = np.dot(delta3, Theta2.T) * self.__sigmoid_gradient(
                np.r_[0, z2[t, :]])
            delta2 = delta2[1:]
            Delta1 = np.outer(np.r_[1, X[t, :]], delta2)
            D1 += Delta1
            D1[1:, :] += lambda_ * Theta1[1:, :]
        logging.info('J: {}.'.format(cost))
        return cost, D1, D2

    def __sigmoid_gradient(self, z):
        g = self.__sigmoid(z)
        return g * (1 - g)

    def __scipy_J_and_gradient(self, theta, X, Y, lambda_):
        Theta1, Theta2 = self.separate_theta(theta)
        J, D1, D2 = self.J_and_gradient(Theta1, Theta2, X, Y, lambda_)
        return J, self.merge_matrix(D1, D2)

    def fit(self, image_models, lambda_):
        init_theta = self.init_theta()
        X = np.array([
            Image(util.get_image_path(img.hashsum, img.filetype)).to_x()
            for img in image_models
        ])
        Y = np.array([Rank(img.rank).to_y() for img in image_models])
        J0, _ = self.__scipy_J_and_gradient(init_theta, X, Y, lambda_)
        result = minimize(
            self.__scipy_J_and_gradient,
            x0=init_theta,
            args=(X, Y, lambda_),
            jac=True,
            method='CG',
            options={'maxiter': 200})

        logging.info('result: {}'.format(result))
        self.__save_theta(result.x)
        # self.__save_J(image_model.hashsum, predict_rank, rank, lambda_, J0,
        #               result.fun)

    def __save_J(selt, hashsum, predict_rank, rank, lambda_, J0, J1):
        with open(CONFIG.J_file, mode='a') as f:
            print(
                '{},{},{},{},{},{}'.format(hashsum, predict_rank, rank,
                                           lambda_, J0, J1),
                file=f)

    def predict(self, image_model):
        x = Image(
            util.get_image_path(image_model.hashsum,
                                image_model.filetype)).to_x()
        return self.__predict(x)

    def __predict(self, x):
        Theta1, Theta2 = self.separate_theta(self.init_theta())
        z2 = np.dot(np.r_[1, x], Theta1)
        a2 = self.__sigmoid(z2)
        z3 = np.dot(np.r_[1, a2], Theta2)
        a3 = self.__sigmoid(z3)
        return a3.argmax() + 1


NETWORK = Network()
