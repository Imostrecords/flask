from flask import Flask, jsonify, request, abort
from datetime import datetime

app = Flask(__name__)

# Хранилище для событий
events = {}

# Модель данных "Событие"
class Event:
    def __init__(self, event_id, date, title, text):
        self.event_id = event_id
        self.date = date
        self.title = title
        self.text = text

# Проверка уникальности события по дате
def is_date_taken(date):
    return date in events

# 1. Создание события
@app.route('/api/v1/calendar', methods=['POST'])
def create_event():
    data = request.json
    date_str = data.get('date')
    title = data.get('title')
    text = data.get('text')

    # Проверка длины заголовка и текста
    if len(title) > 30 or len(text) > 200:
        return jsonify({'error': 'Заголовок не должен превышать 30 символов и текст 200 символов.'}), 400

    # Проверка на наличие события на ту же дату
    if is_date_taken(date_str):
        return jsonify({'error': 'Событие на эту дату уже существует.'}), 400

    # Создание события
    event_id = len(events) + 1
    event = Event(event_id, date_str, title, text)
    events[date_str] = event

    return jsonify({'message': 'Событие добавлено.', 'event_id': event.event_id}), 201

# 2. Получение списка событий
@app.route('/api/v1/calendar', methods=['GET'])
def get_events():
    return jsonify([{ 
        'id': event.event_id,
        'date': event.date,
        'title': event.title,
        'text': event.text 
    } for event in events.values()]), 200

# 3. Чтение события по ID
@app.route('/api/v1/calendar/<int:event_id>', methods=['GET'])
def get_event(event_id):
    for event in events.values():
        if event.event_id == event_id:
            return jsonify({
                'id': event.event_id,
                'date': event.date,
                'title': event.title,
                'text': event.text 
            }), 200
    abort(404)

# 4. Обновление события по ID
@app.route('/api/v1/calendar/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.json
    new_date_str = data.get('date')
    new_title = data.get('title')
    new_text = data.get('text')

    for event in events.values():
        if event.event_id == event_id:
            if new_date_str:
                if is_date_taken(new_date_str) and new_date_str != event.date:
                    return jsonify({'error': 'Событие на эту дату уже существует.'}), 400
                else:
                    del events[event.date]  # Удаляем старое событие по дате
            
            # Обновляем данные события
            if new_title and len(new_title) <= 30:
                event.title = new_title
            
            if new_text and len(new_text) <= 200:
                event.text = new_text
            
            if new_date_str:
                event.date = new_date_str
            
            events[new_date_str] = event  # Сохраняем событие с новой датой (если изменена)
            return jsonify({'message': 'Событие обновлено.'}), 200
    
    abort(404)

# 5. Удаление события по ID
@app.route('/api/v1/calendar/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    for date_key in list(events.keys()):
        if events[date_key].event_id == event_id:
            del events[date_key]
            return jsonify({'message': 'Событие удалено.'}), 204
    
    abort(404)

if __name__ == '__main__':
    app.run(debug=True)