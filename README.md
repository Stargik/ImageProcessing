# ImageProcessing

Проєкт для ручної обробки зображень на Python з GUI (`tkinter`) та Pillow.

## Вимоги

- Python 3.10+
- `tkinter` (вбудований у стандартну поставку Python на більшості систем)

## Швидкий старт (macOS / zsh)

```bash
cd /Users/aleksandrstarzhynskyi/Repositories/Git/GitHub/ImageProcessing
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Якщо `.venv` вже створений

```bash
cd /Users/aleksandrstarzhynskyi/Repositories/Git/GitHub/ImageProcessing
source .venv/bin/activate
python main.py
```

## Вихід із віртуального середовища

```bash
deactivate
```

## Важливо

- Обробка пікселів реалізована вручну через `Image.load()` і вкладені цикли `for`.
- Використовується тільки Pillow для завантаження, відображення та збереження зображень.
