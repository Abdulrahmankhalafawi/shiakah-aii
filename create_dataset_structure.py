import os

def create_dataset_folders():
    # قائمة بالفئات الأساسية للملابس
    categories = ['blazer', 'shirt', 'pants', 'dress', 'shoes']
    base_dir = 'dataset'
    
    print("جاري إنشاء هيكل ملفات الـ Dataset...")
    
    for category in categories:
        dir_path = os.path.join(base_dir, category)
        os.makedirs(dir_path, exist_ok=True)
        print(f"تم إنشاء الفولدر: {dir_path}")
        
    print("\nتم الانتهاء بنجاح! 🎉")
    print("أنت جاهز دلوقتي تحط صور كل فئة جوه الفولدر الخاص بيها.")

if __name__ == '__main__':
    create_dataset_folders()