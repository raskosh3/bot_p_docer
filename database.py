import json
import os
from typing import Dict, List, Any


class Database:
    def __init__(self, filename: str = 'users_data.json'):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def _read_data(self) -> Dict[str, Any]:
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_data(self, data: Dict[str, Any]):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_user_cart(self, user_id: int) -> List[Dict[str, Any]]:
        data = self._read_data()
        return data.get(str(user_id), {}).get('cart', [])

    def add_to_cart(self, user_id: int, product: Dict[str, Any]):
        data = self._read_data()
        user_id_str = str(user_id)

        if user_id_str not in data:
            data[user_id_str] = {'cart': []}

        cart = data[user_id_str]['cart']
        # Проверяем, есть ли уже такой продукт в корзине
        for item in cart:
            if (item['category'] == product['category'] and
                    item['product_key'] == product['product_key']):
                item['quantity'] += 1
                break
        else:
            product['quantity'] = 1
            cart.append(product)

        self._write_data(data)

    def remove_from_cart(self, user_id: int, product_key: str, category: str):
        data = self._read_data()
        user_id_str = str(user_id)

        if user_id_str in data:
            cart = data[user_id_str]['cart']
            data[user_id_str]['cart'] = [
                item for item in cart
                if not (item['product_key'] == product_key and item['category'] == category)
            ]
            self._write_data(data)

    def clear_cart(self, user_id: int):
        data = self._read_data()
        user_id_str = str(user_id)

        if user_id_str in data:
            data[user_id_str]['cart'] = []
            self._write_data(data)

    def update_user_info(self, user_id: int, user_info: Dict[str, str]):
        data = self._read_data()
        user_id_str = str(user_id)

        if user_id_str not in data:
            data[user_id_str] = {'cart': [], 'user_info': {}}

        data[user_id_str]['user_info'] = user_info
        self._write_data(data)

    def get_user_info(self, user_id: int) -> Dict[str, str]:
        data = self._read_data()
        return data.get(str(user_id), {}).get('user_info', {})