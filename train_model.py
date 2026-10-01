import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader

def train_fashion_model():
    # 1. إعداد مسار الـ Dataset وتحويلات الصور (Resize & Normalization) للموديل
    data_dir = 'dataset'
    
    # التأكد من وجود صور في الفولديرات قبل التدريب
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print("❌ تنبيه: فولدر الـ dataset فارغ! يرجى وضع بعض صور الملابس داخل فولديرات الفئات أولاً.")
        return

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # تحميل الصور من فولديرات الفئات أوتوماتيكياً
    dataset = datasets.ImageFolder(root=data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
    
    class_names = dataset.classes
    num_classes = len(class_names)
    print(f"📂 الفئات المكتشفة للتدريب: {class_names}")

    if num_classes == 0:
        print("❌ لا توجد فئات أو صور للتدريب.")
        return

    # 2. تحميل موديل ذكي جاهز (MobileNetV2) وتعديل الطبقة الأخيرة لتناسب ملابسنا
    print("🤖 جاري تحميل وتجهيز نموذج الذكاء الاصطناعي...")
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    
    # تجميد الطبقات السابقة للموديل للاستفادة من ذكائه العام
    for param in model.parameters():
        param.requires_grad = False

    # تعديل طبقة التصنيف الأخيرة لتطابق عدد فئاتنا (قميص، بليزر، إلخ)
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)

    # 3. إعداد دالة الخسارة (Loss) والمحسن (Optimizer)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)

    # 4. حلقة التدريب (Training Loop) المبسطة
    model.train()
    num_epochs = 5  # عدد دورات التدريب (يمكن زيادتها لاحقاً)
    
    print("🚀 بدء تدريب الموديل الآن...")
    for epoch in range(num_epochs):
        running_loss = 0.0
        for images, labels in dataloader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            
        print(f"الورة رقم [{epoch+1}/{num_epochs}] - نسبة الخطأ (Loss): {running_loss/len(dataloader):.4f}")

    # 5. حفظ الموديل المدرب للاستخدام في السيرفر
    torch.save({
        'model_state_dict': model.state_dict(),
        'class_names': class_names
    }, 'fashion_model.pth')
    
    print("🎉 تم تدريب الموديل وحفظه بنجاح في ملف 'fashion_model.pth'!")

if __name__ == '__main__':
    train_fashion_model()