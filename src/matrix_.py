# coding=utf-8
from copy import deepcopy
import copy
import math

def create_by_mn(m,n,_value):
    _mat = []
    for i in range(m):
        _mat.append([_value]*n)
    return _mat

def create_one_mn(m,n):
    _mat = []
    for i in range(m):
        _mat.append([0.1]*n)
    return _mat

def create(_list):
    #int to float
    for r in range(len(_list)):
        for c in range(len(_list[0])):
            #_list[r][c] = float(_list[r][c])
            #decimal.getcontext().prec = 25
            _list[r][c] = float(_list[r][c]) #Deimal
    return _list

def multiply(A,B):
    m1,n1 = shape(A)
    m2,n2 = shape(B)
    A_multi_B = [[0] * len(B[0]) for i in range(len(A))]
    if (n1 == m2):
        for i in range(m1):
            for j in range(n2):
                for k in range(m2):
                    A_multi_B[i][j] += A[i][k]*B[k][j]
        return A_multi_B

def n_mat(n,_A):
    A = deepcopy(_A)
    m, n = shape(A)
    for i in range(m):
        for j in range(n):
            A[i][j] = n*A[i][j]
    return A

def add(A,B):
    A_add_B = []
    m1,n1 = shape(A)
    m2,n2 = shape(B)
    if ((m1 != m2)|(n1 != n2)):
        raise OverflowError
    else:
        for i in range(m1):
            A_add_B.append([])
        for i in range(m1):
            for j in range(n1):
                A_add_B[i].append(A[i][j] + B[i][j])
        return A_add_B

def sub(A,B):
    A_sub_B = []
    m1,n1 = shape(A)
    m2,n2 = shape(B)
    if ((m1 != m2)|(n1 != n2)):
        raise OverflowError
    else:
        for i in range(m1):
            A_sub_B.append([])
        for i in range(m1):
            for j in range(n1):
                A_sub_B[i].append(A[i][j] - B[i][j])
        return A_sub_B

def transpose(A):
    m,n = shape(A)
    _mat = create_by_mn(n,m,0)
    for i in range(m):
        for j in range(n):
            _mat[j][i] = A[i][j]
    return _mat

def inverse(_A):
    #A = _A[:]
    A = deepcopy(_A)
    # elimate the principal of column
    # create [A,E]
    A_I = []
    m = len(A)
    E = eye(m)
    A = extend(A,E)
    ### swap the row
    for c in range(m):  #  column
        max_row = c
        max_num = float(0)
        for r in range(c,m): # row
            if A[r][c] >= max_num:
                max_row = r
                max_num = A[r][c]
        if max_row != c:
            A[c],A[max_row] = A[max_row],A[c]
        ## elimination elements
        if A[c][c] == 0:
            return 0
        elimination(A,c,c,m,m)
        #print show(A)
    for row in A:
        A_I.append(row[m:])
    return A_I

def solve(_A,_B):
    _X = []
    m_a = len(_A)
    m_b = len(_B)
    A = extend(_A, _B)
### swap the row
    for c in range(m_a):  #  column
        max_row = c
        max_num = float(0)
        for r in range(c,m_a): # row
            if A[r][c] >= max_num:
                max_row = r
                max_num = A[r][c]
        if max_row != c:
            A[c],A[max_row] = A[max_row],A[c]
        ## elimination elements
        if A[c][c] == 0:
            return 0
        elimination(A,c,c,m_a,m_b)
        #print show(A)
    for row in A:
        _X.append(row[m_a:])
    return _X

def elimination(A,_row,_column,m_a,m_b):
    max_num = (A[_row][_column])
    for c in range(m_a+m_b):
        A[_row][c] = (A[_row][c])/max_num

    for r in range(len(A)):
        if r != _row:
            rate = A[r][_column]
            for c in range(m_a+m_b):
                A[r][c] = A[r][c]-rate*A[_row][c]

def sparse_inverse(_A):
    A = deepcopy(_A)
    A_T = transpose(A)
    A_I = solve(multiply(multiply(A, A_T),A), multiply(A, A_T))
    return A_I

def shape(A):
    if A is None or len(A) == 0:
        return (0,0)
    return (len(A),len(A[0]))

def eye(_m):
    #create unit matrix
    E = create_by_mn(_m, _m, 0)
    i=0
    for row in E:
        row[i] = 1.0
        i = i+1
    return E

def det(A):
    pass

def extend(_A,_B):
    # create [A,B]
    A = deepcopy(_A)
    if len(A) == len(_B):
        for i in range(len(A)):
            A[i].extend(_B[i])
    return create(A)

def show(A):
    for colum in A:
        print len(colum),colum

''' lasso '''
#前向逐步回归归一化处理：：：：特殊情况下的减法，其中B是行向量，结果应该为A的每一行减去行向量B
def lasso_sub(A,B):
    A_sub_B = []
    m1,n1 = shape(A)
    m2,n2 = shape(B)
    if (n1 != n2):
        raise ValueError
    else:
        for i in range(m1):
            A_sub_B.append([])
        for i in range(1,m1):
            B.append(B[0])

        for i in range(m1):
            for j in range(n1):
                A_sub_B[i].append(A[i][j] - B[i][j])
        return A_sub_B

#前向逐步回归归一化处理：：：：特殊情况下的除法，其中B是行向量，结果应该为A的每一行的各个元素分别除以行向量B的对应元素
def divise(A,B):
    A_div_B = []
    m1,n1 = shape(A)
    m2,n2 = shape(B)
    if (n1 != n2):
        raise ValueError
    else:
        for i in range(m1):
            A_div_B.append([])
        for i in range(1,m1):
            B.append(B[0])

        for i in range(m1):
            for j in range(n1):
                A_div_B[i].append(float(A[i][j]) / B[i][j])
        return A_div_B

#计算两个矩阵(1*n)的平方误差之和
def rssError(A, B):
    m1,n1 = shape(A)
    m2,n2 = shape(B)
    sum_error = float(0)
    if m1==m2 and n1==n2:
        for i in range(m1):
            for j in range(n1):
                single = (A[i][j] - B[i][j])**2
                sum_error += single
        return sum_error
    else:
        raise ValueError

def list_add(list,i,j,value):
    start = list[i][j]
    end = start+value
    list[i][j] = end
    return list

def assign(_A,_B):
    # 将Ｂ的值赋给Ａ
    m1,n1 = shape(_A)
    m2,n2 = shape(_B)
    if m1==m2 and n1==n2:
        for i in range(m1):
            for j in range(n1):
                _A[i][j] = _B[i][j]
    else:
        raise ValueError


def data_normarlization(_A):
    pass

'''regtree'''

def choice_row(_A,_m):
    return _A[_m]

def choice_column(_A,_n):
    column_A = []
    for line in _A:
        column_A.append(line[_n])
    return column_A

def muiltipy_by(_A,_num):
    _A_by = copy.deepcopy(_A)
    m, n = shape(_A_by)
    for i in range(m):
        for j in range(n):
            _A_by[i][j] = _A_by[i][j]*_num
    return _A_by

def get_sum(_A):
    sum = 0
    m, n = shape(_A)
    for i in range(m):
        for j in range(n):
            sum += _A[i][j]
    return sum

def mean(_A):
    if type(_A[0]) == list:
        m,n = shape(_A)
        sum = get_sum(_A)
        return float(sum)/(m*n)
    else:
        sum = 0
        for item in _A:
            sum += item
        return float(sum)/len(_A)

def var(_A):
    sum = 0
    _A_mean = mean(_A)
    if type(_A[0]) == list: #二维列表
        m, n = shape(_A)
        for i in range(m):
            for j in range(n):
                sum += (_A[i][j]-_A_mean)**2
        return float(sum)/(m*n)
    else: #一维列表
        for item in _A:
            sum += (item-_A_mean)**2
        return float(sum)/(len(_A))

def dot(X1,X2):
    # dot
    if len(X1)!= len(X2):
        raise ValueError
    sum = 0
    for i in range(len(X1)):
        sum += X1[i]*X2[i]
    return sum

def tanh(x):
    x = float(x)
    print "e: x:",x
    result = (math.exp(x)-math.exp(-1.0*x))/(math.exp(x)+math.exp(-1.0*x))
    # print "tanh: ",result
    return result


