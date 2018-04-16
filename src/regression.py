# -*- coding: UTF-8 -*-
import matrix_ as mat
from matrix_ import show
import copy
import math
import cart

"""
算法实现，供使用的算法有：岭回归,核岭回归,代替lasso的逐步向前,树回归
"""

class Regression(object):
    #前向逐步回归算法构造函数
    def __init__(self,X,y):
        self.isError = False
        X = mat.create(X)
        y = mat.create(y)
        # self.w ,self.old_X= self.kernal_ridge_train(X,y,1.0)  #核岭回归
        self.w = self.ridge_train(X,y,0.5) # 岭回归
        '''
        # 回归树
        self.old_X = X
        X_K = self.Kernal(X)  # 核函数映射,低维映射到高维
        print "X_K:\n",show(X_K)
        dateset = cart.make_dateSet(X_K,y)
        self.regtree = cart.createTree(dateset)
        '''

    def ridge_train(self,X,y,alpha):
        """
        :param X: 输入的特征矩阵
        :param y: 输入的标签
        :param alpha: a complexity parameter that controls the amount of shrinkage
        :return:　模型的权重系数
        w = (X.T*X+alpha*I).I*X.T*y
        """
        m,n = mat.shape(X)
        B = mat.create_by_mn(m,1,1.0)
        X = mat.extend(X,B) # 将偏bias系数合并
        X_T = mat.transpose(X)
        X_T_X = mat.multiply(X_T,X)
        m,n = mat.shape(X_T_X)
        I = mat.eye(m)
        alp_I =mat.n_mat(alpha,I)
        _inverse = mat.inverse(mat.add(X_T_X,alp_I))
        if _inverse == 0:
            self.isError = True
            print("逆矩阵不可求")
            return 0
        _w =mat.multiply(mat.multiply(_inverse,X_T),y)
        return _w

    def predict_ridge(self,_new_X):
        if self.isError == True:
            return 0
        _new_X = mat.create(_new_X)
        _new_X = mat.extend(_new_X,[[1.0]])
        return mat.multiply(_new_X,self.w)

    def kernal_ridge_train(self,X,y,alpha):
        m,n = mat.shape(X)
        B = mat.create_by_mn(m,1,1.0)
        X = mat.extend(X,B)
        X_K = self.Kernal(X)  # 核函数映射,低维映射到高维
        X_T = mat.transpose(X_K)
        X_T_X = mat.multiply(X_T,X_K)
        m,n = mat.shape(X_T_X)
        I = mat.eye(m)
        alp_I =mat.n_mat(alpha,I)
        _inverse = mat.inverse(mat.add(X_T_X, alp_I))
        if _inverse == 0:
            self.isError = True
            print("逆矩阵不可求")
            return 0,0
        _w = mat.multiply(mat.multiply(_inverse, X_T), y)
        return _w,X

    def predict_kernal_ridge(self,_new_X):
        if self.isError == True:
            return 0
        _new_X = mat.create(_new_X)
        _new_X = mat.extend(_new_X,[[1.0]])
        del self.old_X[0]  # 删除第一条
        self.old_X.append(_new_X[0]) # add a new one
        #print "self.old_X: ",self.old_X
        _X_K = self.Kernal(self.old_X)
        predict_y = mat.multiply(_X_K,self.w)
        #print "predict_y: ",predict_y
        return [predict_y[-1]]

    def Kernal(self,X):
        X_K = []
        row = len(X)
        for i in range(row): # row
            X_K_r = []
            for j in range(row): # row
                X_K_r.append(self.rbf(X[i],X[j]))
            X_K.append(X_K_r)
        return X_K

    def rbf(self,X1,X2,sigma=90):
        """
        :param X1: 一个特征样本
        :param X2: 一个特征样本
        :param sigma:
        :return:高斯核计算结果
        """
        # X1,X2 矩阵的代表一行
        if len(X1) != len(X2):
            raise ValueError
        X1_sub_X2 = []
        for i in range(len(X1)):
            X1_sub_X2.append(X1[i]-X2[i])
        L2 = 0
        for item in X1_sub_X2:
            L2 += math.fabs(item)#**2
        return math.exp(-1*L2/float(2*sigma**2))
        # return math.exp(-1*sigma*L2)

    def sigmoid(self,X1,X2):
        # sigmoid 核
        return mat.tanh(0.1*mat.dot(X1,X2)-1)

    def poly(self,X1,X2):
        # 多项式核
        if len(X1) != len(X2):
            raise ValueError
        #print "dot: ",mat.dot(X1,X2)
        return (mat.dot(X1,X2)+1)**(2)

    def laplacian(self,X1,X2,gamma =50):
        # 拉普拉斯核
        X1_sub_X2 = []
        for i in range(len(X1)):
            X1_sub_X2.append(X1[i] - X2[i])
        L1 = 0
        for item in X1_sub_X2:
            L1 += math.fabs(item)
        return math.exp(-1 * L1 / float(gamma))

    def linear(self,X1,X2):
        # 线性核
        result = 0
        if len(X1)!=len(X2):
            raise OverflowError
        for i in range(len(X1)):
            result += X1[i]*X2[i]
        return result

    def predict_regtree(self,_new_X):
        # 树回归预测
        # input: _new_X：[[...]]s
        # _new_X = mat.create(_new_X)
        #print "_new_X:",_new_X
        del self.old_X[0]  # 删除第一条
        self.old_X.append(_new_X[0]) # add a new one
        #print "self.old_X: ",mat.show(self.old_X)
        #assert 0
        _X_K = self.Kernal(self.old_X)
        value = cart.forecastSample(self.regtree,[_X_K[-1]])
        return [[value]]

    '''
    前向逐步线性回归
    xArr为输入的数据，yArr为预测的变量
    eps为步长，numIt为迭代次数
    '''
    def lasso_predict(self,_new_X):
        _new_X = mat.create(_new_X)
        return mat.multiply(_new_X, self.w)

    def lasso_train(self,X,y):
        _w = self.stageWise(X, y)
        return _w

    def stageWise(self,xArr,yArr,eps=0.01,numIt=5000):
        xMat = xArr
        yMat = yArr#预测的变量的转置
        yMean=mat.mean(yMat,0)
        yMat=mat.lasso_sub(yMat,yMean)
        xMat=mat.regularize(xMat)
        m,n=mat.shape(xMat)
        print xMat,yMat

        ws=mat.create_one_mn(n,1)
        # tempws = copy.deepcopy(ws)
        # lowestError = float("inf")  # float("inf") #初始化当前迭代的最小误差表示为正无穷大
        for a_weight in ws:
            lowestError = float("inf")
            #mat.assign(tempws, ws)
            forward = 1
            old_rssE = mat.rssError(yMat, mat.multiply(xMat, ws))
            a_weight[0] = a_weight[0] + eps*forward
            rssE = mat.rssError(yMat, mat.multiply(xMat, ws))
            if rssE > old_rssE:
                forward = -1

            for time in range(numIt):
                a_weight[0] = a_weight[0] + eps * forward
                new_error = mat.rssError(yMat, mat.multiply(xMat, ws))
                if new_error > old_rssE:
                    break
                old_rssE = new_error
        print "ws: \n",ws
        return ws

        for i in range(numIt):
            ##每一次迭代
            for j in range(n):
                a1 = tempws[j][0]
                a2 = a1
                # 遍历每一个特征
                for sign in [-1, 1]:  # 两次循环，计算增加或者减少该特征对误差的影响
                    tempws[j][0] = a1
                    b = float(eps * sign)
                    tempws = mat.list_add(tempws, j, 0, b)
                    yTest = mat.multiply(xMat, tempws)
                    rssE = mat.rssError(yMat, yTest)  # 平方误差,将矩阵转换成为数组Array
                    if rssE < lowestError:
                        lowestError = rssE
                        a2 = tempws[j][0]
                        mat.assign(ws, tempws)
                if a2 != a1:
                    tempws[j][0] = a2
                else:
                    tempws[j][0] = a1
