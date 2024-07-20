import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch.multiprocessing as mp
# 自定义数据集类
# 自定义数据集类
class CustomDataset(Dataset):
    def __init__(self, img_file, label_file, transform=None):
        # 读取 CSV 文件中的数据，指定数据类型
        img_df = pd.read_csv(img_file, dtype={0: str}, low_memory=False)
        img_df.iloc[:, 1:] = img_df.iloc[:, 1:].astype(np.int64)

        label_df = pd.read_csv(label_file, dtype={0: str, 1: np.int64}, low_memory=False)

        # 提取 ID 和图像数据
        self.img_ids = img_df.iloc[:, 0].values
        self.img_data = img_df.iloc[:, 1:].values

        # 提取标签 ID 和类别
        self.label_ids = label_df.iloc[:, 0].values
        self.labels = label_df.iloc[:, 1].values
        # 创建一个字典用于快速查找标签
        self.label_dict = dict(zip(self.label_ids, self.labels))

        # 根据图像 ID 找到对应的标签
        self.images = []
        self.targets = []

        for idx, img_id in enumerate(self.img_ids):
            if img_id in self.label_dict:
                self.images.append(self.img_data[idx])
                self.targets.append(self.label_dict[img_id])
        # 转换为 numpy 数组
        self.images = np.array(self.images)
        self.targets = np.array(self.targets)
        self.transform = transform


    def __len__(self):
        return len(self.targets)

    def __getitem__(self, idx):
        # 将每行数据重塑为 50x30 图像
        image = self.images[idx].reshape(50, 30).astype(np.uint8)
        label = self.targets[idx]

        if self.transform:
            image = self.transform(image)

        return image, label


# 数据变换
transform = transforms.Compose([
    transforms.ToPILImage(),  # 将 numpy 数组转换为 PIL 图像
    transforms.ToTensor(),  # 将 PIL 图像转换为张量
    transforms.Normalize((0.5,), (0.5,))  # 归一化
])

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(32 * 12 * 7, 128)  # 计算池化后的尺寸
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)  # 假设有 9 个类别

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.pool2(x)
        x = x.view(-1, 32 * 12 * 7)  # 计算池化后的尺寸
        x = self.fc1(x)
        x = self.relu3(x)
        x = self.fc2(x)
        return x

model_state_dict = torch.load('modelX.pt')
model = CNN()
model.load_state_dict(model_state_dict)
model.eval()  # 设置模型为评估模式，这会关闭dropout和batch normalization


    # 用于存储预测结果的列表
    # predictions = []
    # targets_list = []

    # with torch.no_grad():
    #     for inputs, targets in test_loader:  # Assuming you have a DataLoader for your test set
    #         # print(inputs,targets)
    #         outputs = model(inputs)
    #         print(outputs)
            #loss = criterion(outputs, targets)
  
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report    
from os import listdir, mkdir
from os.path import basename, exists
from tqdm import tqdm
from shutil import rmtree
def test_single(asm, eval_mode=False):
    asm_basename = basename(asm)
# 创建数据集和数据加载器
    if eval_mode:
        test = CustomDataset(asm, 'TrainLabels_cnn.csv',transform=transform)
    else:
        if not exists('./tmp'):
            mkdir('./tmp')
        with open('./tmp/'+asm_basename.split('.')[0]+'.csv', 'w') as f:
            f.write('"Id","Class"\n')
            f.write('"'+asm_basename.split('.')[0]+'.asm"'+',99')
        test = CustomDataset(asm, './tmp/'+asm_basename.split('.')[0]+'.csv',transform=transform)
    test_loader = DataLoader(test, batch_size=1, shuffle=False, num_workers=2,drop_last=True)

    predictions = []
    targets_list = []
    with torch.no_grad():
        for inputs, targets in test_loader:  # Assuming you have a DataLoader for your test set
        # 下面是评估用代码(也是放for遍历中)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)  # 获取预测类别索引
            predictions.extend(predicted.cpu().numpy())
            targets_list.extend(targets.cpu().numpy())
            if eval_mode:
                if predictions[0] == targets_list[0]:
                    return (targets_list, False)
                else:
                    return (targets_list, True)
            else:
                rmtree('./tmp')
                return predictions[0]
if __name__ == '__main__':
    def test_cnn():
        import csv

# 假设CSV文件的路径
        csv_file = 'TrainLabels_cnn.csv'

        # 要提取的列的索引（假设第二列，索引从0开始）
        column_index = 1

        # 用于存储列数据的列表
        column_data = []

        # 打开CSV文件
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.reader(file)
            # 遍历每一行，提取特定列的数据
            for row in reader:
                # 确保行的长度足够长，避免索引错误
                if len(row) > column_index:
                    column_data.append(row[column_index])
        
        test1coor = [0, column_data.count(0)]
        test2coor = [0, column_data.count(1)]
        test3coor = [0, column_data.count(2)]
        test4coor = [0, column_data.count(3)]
        test5coor = [0, column_data.count(4)]
        test6coor = [0, column_data.count(5)]
        test7coor = [0, column_data.count(6)]
        test8coor = [0, column_data.count(7)]
        test9coor = [0, column_data.count(8)]
        testcoor = [test1coor, test2coor, test3coor, test4coor, test5coor, test6coor, test7coor, test8coor, test9coor]
        for asm in tqdm(listdir('./test_cnn')):
            result = test_single('./test_cnn/'+asm, eval_mode=True)
            if result[1]:
                testcoor[result[0][0]][0]+=1
        print(testcoor)
    # test_cnn()
    # print(test_single('./upload/0aKlH1MRxLmv34QGhEJP.asm_imgfeature.csv'))
# # 将列表转换为numpy数组（如果需要的话），但这里通常不是必需的，因为scikit-learn函数可以处理列表
#     predictions = np.array(predictions)
#     targets = np.array(targets_list)


#     # 下面二选一
#     # # 计算评估指标
#     accuracy = accuracy_score(targets_list, predictions)
#     print(f"Accuracy: {accuracy:.4f}")


# 如果使用了classification_report，则取消注释以下行
# print(classification_report(targets_list,predictions , digits=4))





