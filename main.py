import sys
import random
import csv
from typing import List, Tuple
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QMessageBox, QRadioButton, QButtonGroup, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt

CSV_PATH = "words.csv"

# РАСШИРЕННЫЕ ПРАВИЛА
RULES = {
    1: "<b>Безударные гласные в корне:</b><br><br>Чтобы проверить безударную гласную в корне слова, нужно изменить слово или подобрать однокоренное так, чтобы эта гласная стала ударной.<br><i>Пример: гора́ — го́ры, вода́ — во́ды.</i>",
    2: "<b>Словарные слова:</b><br><br>Написание этих слов нельзя проверить правилом. Их нужно запомнить или проверять по орфографическому словарю.<br><i>Пример: винегрет, интеллект, коварство.</i>",
    3: "<b>Суффиксы (основные правила):</b><br><br>"
       "1. <b>-ЕК- / -ИК-:</b> Пишем И, если при склонении гласная сохраняется (ключик — ключика), и Е, если она 'убегает' (замочек — замочка).<br>"
       "2. <b>О / Е после шипящих:</b> В суффиксах сущ. и прил. под ударением пишем О (волчонок), без ударения — Е (реченька).<br>"
       "3. <b>-ИВ- / -ЕВ-:</b> В прилагательных под ударением И (красивый), без ударения — Е (боевой). Исключения: милостивый, юродивый.<br>"
       "4. <b>-ЧИК- / -ЩИК-:</b> Пишем -ЧИК- после согласных т, д, з, с, ж (извозчик), в остальных случаях — -ЩИК- (банщик).",
    4: "<b>Непроизносимые согласные:</b><br><br>Для проверки нужно подобрать однокоренное слово, где этот согласный слышится отчетливо перед гласным или на конце слова.<br><i>Пример: честный — честь, солнце — солнышко, грустный — грусть.</i>",
    5: "<b>Микс:</b><br><br>Здесь собраны задания по всем изученным темам. Будьте внимательны, вспоминайте правила для каждого конкретного слова!"
}

STYLESHEET = """
    MainWindow, MainMenu, TestWindow, ResultWindow, RuleWindow { 
        background-color: #F1F5F9; 
    }
    QFrame#Card { background-color: white; border-radius: 15px; border: 2px solid #E2E8F0; }
    QLabel#Title { font-size: 22px; font-weight: bold; color: #1E293B; margin-bottom: 10px; }
    QLabel#Text { font-size: 18px; color: #334155; }

    QPushButton#MenuBtn {
        background-color: white; border: 2px solid #6366F1; color: #4338CA;
        border-radius: 10px; padding: 12px; font-size: 16px; font-weight: bold;
    }
    QPushButton#RuleBtn {
        background-color: #EEF2FF; border: 2px solid #6366F1; color: #6366F1;
        border-radius: 10px; font-size: 18px; font-weight: bold;
    }
    QPushButton#MenuBtn:hover, QPushButton#RuleBtn:hover { background-color: #6366F1; color: white; }

    QRadioButton { font-size: 18px; padding: 10px; color: #1E293B; }
    QRadioButton::indicator { width: 20px; height: 20px; border: 2px solid #6366F1; border-radius: 12px; background-color: white; }
    QRadioButton::indicator:checked { background-color: #6366F1; border: 4px solid white; }

    QPushButton#ConfirmBtn {
        background-color: #10B981; color: white; border-radius: 10px;
        padding: 15px 40px; font-size: 18px; font-weight: bold; border: none;
    }
    QPushButton#ConfirmBtn:hover { background-color: #059669; }
"""


class DataManager:
    def __init__(self, path: str = CSV_PATH):
        self.path = path

    def load_questions(self, category_id: int, limit: int = 10) -> List[Tuple]:
        questions = []
        try:
            with open(self.path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 5:
                        try:
                            row_cat_id = int(row[-1].strip())
                            if category_id == 5 or row_cat_id == category_id:
                                questions.append(tuple(row[:4]))
                        except:
                            continue
        except FileNotFoundError:
            return []
        random.shuffle(questions)
        return questions[:limit]


class RuleWindow(QWidget):
    def __init__(self, main_window, category_id, title):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        card = QFrame();
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        lbl_t = QLabel(f"Правило: {title}");
        lbl_t.setObjectName("Title");
        lbl_t.setWordWrap(True)
        txt = QLabel(RULES.get(category_id, "Текст отсутствует."));
        txt.setObjectName("Text");
        txt.setWordWrap(True)

        card_layout.addWidget(lbl_t);
        card_layout.addWidget(txt);
        card_layout.addStretch()
        layout.addWidget(card)

        btn = QPushButton("ПОНЯТНО");
        btn.setObjectName("ConfirmBtn")
        btn.clicked.connect(main_window.back_to_menu)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)


class TestWindow(QWidget):
    def __init__(self, main_window, dm, category_id, title):
        super().__init__()
        self.main_window = main_window
        self.questions = dm.load_questions(category_id)
        self.current_index = 0
        self.correct_answers = 0
        self.init_ui(title)

    def init_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)
        header = QLabel(title);
        header.setObjectName("Title");
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        self.card = QFrame();
        self.card.setObjectName("Card")
        card_layout = QVBoxLayout(self.card)
        self.q_label = QLabel();
        self.q_label.setObjectName("Text")
        card_layout.addWidget(self.q_label)
        self.group = QButtonGroup(self)
        self.btns = []
        for i in range(4):
            rb = QRadioButton();
            self.btns.append(rb)
            self.group.addButton(rb, i);
            card_layout.addWidget(rb)
        layout.addWidget(self.card)
        self.next_btn = QPushButton("ОТВЕТИТЬ");
        self.next_btn.setObjectName("ConfirmBtn")
        self.next_btn.clicked.connect(self.handle_next)
        layout.addWidget(self.next_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        if not self.questions:
            QMessageBox.critical(self, "Ошибка", "Нет вопросов.");
            self.main_window.back_to_menu()
        else:
            self.display_q()

    def display_q(self):
        q_data = self.questions[self.current_index]
        self.correct_val = q_data[0]
        options = list(q_data);
        random.shuffle(options)
        self.q_label.setText(f"Вопрос {self.current_index + 1} из {len(self.questions)}:\nВыберите верное написание:")
        self.group.setExclusive(False)
        for btn, text in zip(self.btns, options):
            btn.setChecked(False);
            btn.setText(text)
        self.group.setExclusive(True)

    def handle_next(self):
        btn = self.group.checkedButton()
        if not btn: return QMessageBox.warning(self, "!", "Выберите ответ")
        if btn.text() == self.correct_val: self.correct_answers += 1
        self.current_index += 1
        if self.current_index < len(self.questions):
            self.display_q()
        else:
            self.main_window.show_results(self.correct_answers, len(self.questions))


class ResultWindow(QWidget):
    def __init__(self, main_window, correct, total):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)

        card = QFrame();
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        title = QLabel("ТЕСТ ЗАВЕРШЕН");
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        score_val = f"{correct} из {total}"
        score_lbl = QLabel(f"Ваш результат:\n{score_val}")
        score_lbl.setObjectName("Text")
        score_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #10B981;")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title);
        card_layout.addWidget(score_lbl)
        layout.addWidget(card)

        btn = QPushButton("В ГЛАВНОЕ МЕНЮ");
        btn.setObjectName("ConfirmBtn")
        btn.clicked.connect(main_window.back_to_menu)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)


class MainMenu(QWidget):
    def __init__(self, main_window):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Интерактивный тренажер по орфографии\nрусского языка")
        title.setObjectName("Title");
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        topics = [(1, "Безударные гласные"), (2, "Словарные слова"), (3, "Суффиксы"), (4, "Непроизносимые согласные"),
                  (5, "МИКС")]
        for cid, name in topics:
            row = QHBoxLayout()
            btn_t = QPushButton(name);
            btn_t.setObjectName("MenuBtn")
            btn_t.clicked.connect(lambda ch, i=cid, n=name: main_window.start_test(i, n))
            btn_r = QPushButton("?");
            btn_r.setObjectName("RuleBtn");
            btn_r.setFixedWidth(45)
            btn_r.clicked.connect(lambda ch, i=cid, n=name: main_window.show_rule(i, n))
            row.addWidget(btn_t);
            row.addWidget(btn_r);
            layout.addLayout(row)


class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.dm = DataManager();
        self.setStyleSheet(STYLESHEET)
        self.menu = MainMenu(self);
        self.addWidget(self.menu)
        self.setWindowTitle("Тренажер по орфографии");
        self.resize(700, 600)

    def start_test(self, cat_id, title):
        self.test_win = TestWindow(self, self.dm, cat_id, title)
        self.addWidget(self.test_win);
        self.setCurrentWidget(self.test_win)

    def show_rule(self, cat_id, title):
        self.rule_win = RuleWindow(self, cat_id, title)
        self.addWidget(self.rule_win);
        self.setCurrentWidget(self.rule_win)

    def show_results(self, c, t):
        self.res_win = ResultWindow(self, c, t)
        self.addWidget(self.res_win);
        self.setCurrentWidget(self.res_win)

    def back_to_menu(self): self.setCurrentWidget(self.menu)


if __name__ == "__main__":
    app = QApplication(sys.argv);
    w = MainWindow();
    w.show();
    sys.exit(app.exec())
