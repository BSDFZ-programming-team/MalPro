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

# 创建数据集和数据加载器
train_dataset = CustomDataset('imgfeature_cnn.csv', 'TrainLabels_cnn.csv', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2)


class CNN(nn.Module):
    # 初始化函数 __init__(): 这个函数在创建模型对象时被调用，并用于定义模型的各个层和参数。
    # 在这个函数中，您可以定义卷积层、池化层、全连接层等网络组件，并初始化它们的参数。
    # 您还可以定义一些超参数，如卷积核大小、池化窗口大小、隐藏层的大小等。
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(32 * 30 * 30, 64)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(64, 2)

    # 前向传播函数forward(): 这个函数定义了模型的前向传播过程。
    # 在这个函数中，您需要指定数据从输入层经过各个层的流动方式。
    # 您可以使用卷积操作、池化操作和激活函数等来处理输入数据，并最终生成模型的输出
    def forward(self, x):
        x = self.conv1(x)
        x = self.relu1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.pool2(x)
        x = x.view(-1, 32 * 30 * 30)
        x = self.fc1(x)
        x = self.relu3(x)
        x = self.fc2(x)
        # print(x.shape)
        return x


# 初始化模型、损失函数和优化器
model = CNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)


# 训练函数
def train(model, train_loader, criterion, optimizer, epochs):
    for epoch in range(epochs):
        running_loss = 0.0
        for i, data in enumerate(train_loader, 0):
            inputs, labels = data
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels.long())
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"Epoch {epoch + 1} loss: {running_loss / len(train_loader)}")
    print("Training finished!")


if __name__ == '__main__':
    mp.freeze_support()
    # 训练模型
    train(model, train_loader, criterion, optimizer, epochs=15)

    # 保存模型
    PATH = "modelX.pt"
    torch.save(model.state_dict(), PATH)
    print(f"Model saved to {PATH}")