import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from flask import Flask, render_template, request, jsonify
import sqlite3
from deep_translator import GoogleTranslator

app = Flask(__name__)

MODEL_PATH = 'fashion_model.pth'
device = torch.device('cpu')

model = None
class_names = []

if os.path.exists(MODEL_PATH):
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    class_names = checkpoint.get('class_names', [])
    num_classes = len(class_names)
    
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def predict_image(image_path):
    if not model or not class_names:
        return None
    try:
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0).to(device)
        with torch.no_grad():
            outputs = model(image_tensor)
            _, predicted = torch.max(outputs, 1)
        return class_names[predicted.item()]
    except Exception as e:
        print(f"Prediction Error: {e}")
        return None

# English Outfit Generator Engine
def generate_outfit_suggestion(category):
    suggestions = {
        'blazer': "✨ Outfit Suggestion: Pair it with a plain white t-shirt, black formal trousers, and leather dress shoes.",
        'shirt': "✨ Outfit Suggestion: Matches great with dark blue denim jeans and casual white sneakers.",
        'pants': "✨ Outfit Suggestion: Style it with an oversized shirt or a modern hoodie and comfortable sports shoes.",
        'dress': "✨ Outfit Suggestion: Combine it with a cropped denim jacket and high heels or elegant sandals.",
        'shoes': "✨ Outfit Suggestion: Perfect match with skinny jeans and a graphic casual t-shirt."
    }
    return suggestions.get(category.lower(), "✨ Outfit Suggestion: Style with well-coordinated casual pieces.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        clothing_query = request.form.get('clothing', '').strip()
        image_file = request.files.get('image')
        
        detected_category = None
        
        if image_file and image_file.filename != '':
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(image_path)
            detected_category = predict_image(image_path)

        search_term = clothing_query
        if not search_term and detected_category:
            search_term = detected_category

        # Automatically translate any input language to English for database querying
        translated_query = search_term
        if search_term:
            try:
                translated_query = GoogleTranslator(source='auto', target='en').translate(search_term)
            except Exception as e:
                print(f"Translation error: {e}")

        conn = sqlite3.connect('fashion_stock.db')
        cursor = conn.cursor()
        
        query_pattern = f'%{translated_query}%' if translated_query else '%%'
        cursor.execute('''
            SELECT title, category, style, gender, image_url 
            FROM inventory 
            WHERE title LIKE ? OR category LIKE ? OR style LIKE ?
        ''', (query_pattern, query_pattern, query_pattern))
        
        item = cursor.fetchone()
        conn.close()

        category_to_use = detected_category if detected_category else (item[1] if item else translated_query)
        outfit_tip = generate_outfit_suggestion(category_to_use if category_to_use else 'general')

        if item:
            result_text = f"📦 Stock Item: {item[0]}\n📂 Category: {item[1]}\n🎨 Style: {item[2]}\n\n{outfit_tip}"
        else:
            result_text = f"🤖 AI Classification: {translated_query or 'N/A'}\n\n{outfit_tip}\n(Note: Item is not directly registered in the inventory stock, but the styling recommendation is ready!)"

        if detected_category:
            result_text = f"🔍 [Image successfully recognized by AI]\n\n" + result_text

        return jsonify({'result': result_text})

    except Exception as e:
        print(f"Server Route Error: {e}")
        return jsonify({'result': f"Server Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)