# coding=utf-8
from matrix_ import shape,mean,var,choice_column,extend

# 决策树生成
def make_dateSet(X,y):
    return extend(X,y)

def createTree(dataSet,op=[1,1]):
    bestFeat,bestNumber = choseBestFeature(dataSet,op)
    if bestFeat==None: return bestNumber
    regTree = {}
    regTree['spInd'] = bestFeat
    regTree['spVal'] = bestNumber
    dataL,dataR = dataSplit(dataSet,bestFeat,bestNumber)
    regTree['left'] = createTree(dataL,op)
    regTree['right'] = createTree(dataR,op)
    return  regTree

# 根据给定的特征、特征值划分数据集
def dataSplit(dataSet,feature,featNumber):
    dataL, dataR = [],[]
    for data_line in dataSet:
        if data_line[feature] > featNumber:
            dataL.append(data_line)
        else:
            dataR.append(data_line)
    return dataL,dataR

# 特征划分
def choseBestFeature(dataSet,op = [1,1]):          # 三个停止条件可否当作是三个预剪枝操作
    if len(set(get_label(dataSet)))==1:     # 停止条件 1
        regLeaf = mean(get_label(dataSet))
        return None,regLeaf                   # 返回标签的均值作为叶子节点
    Serror = GetAllVar(dataSet)
    BestFeature = -1; BestNumber = 0; lowError = float('inf')
    m,n = shape(dataSet) # m 个样本， n -1 个特征
    for i in range(n-1):    # 遍历每一个特征值
        for j in set(choice_column(dataSet,i)): # 选择一列
            dataL,dataR = dataSplit(dataSet,i,j)  # 以该列某值划分
            #print dataR,"\n",dataL
            if shape(dataR)[0]<op[1] or shape(dataL)[0]<op[1]: continue  # 如果所给的划分后的数据集中样本数目甚少，则直接跳出
            tempError = GetAllVar(dataL) + GetAllVar(dataR)
            if tempError < lowError:
                lowError = tempError; BestFeature = i; BestNumber = j
    # if Serror - lowError < 0.01:               # 停止条件 2   如果所给的数据划分前后的差别不大，则停止划分
    #     print "Serror,lowError: ",Serror,lowError
    #     print "---",mean(get_label(dataSet))
    #     return None,mean(get_label(dataSet))
    dataL, dataR = dataSplit(dataSet, BestFeature, BestNumber)
    if shape(dataR)[0] < op[1] or shape(dataL)[0] < op[1]:        # 停止条件 3
        return None, mean(get_label(dataSet))
    return BestFeature,BestNumber

# 计算总的方差
def GetAllVar(dataSet):
    return var(get_label(dataSet))*shape(dataSet)[0]

def get_label(_dataSet):
    # 最后一列为标签
    return choice_column(_dataSet,shape(_dataSet)[1]-1)

def forecastSample(Tree,testData):
    if not isTree(Tree): return float(Tree)
    # print"选择的特征是：" ,Tree['spInd']
    # print"测试数据的特征值是：" ,testData[Tree['spInd']]
    if testData[0][Tree['spInd']]>Tree['spVal']:
        if isTree(Tree['left']):
            return forecastSample(Tree['left'],testData)
        else:
            return float(Tree['left'])
    else:
        if isTree(Tree['right']):
            return forecastSample(Tree['right'],testData)
        else:
            return float(Tree['right'])

def isTree(Tree):
    return (type(Tree).__name__=='dict' )

