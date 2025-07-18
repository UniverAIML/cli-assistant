"""
Модуль чат-асистента з використанням трансформерної моделі для обробки природної мови.
Цей модуль забезпечує взаємодію з користувачем через чат-інтерфейс з підтримкою виклику функцій.
"""

import json
import re
from typing import Any, Dict, List, Optional

from colorama import Fore, Style

from .config_manager import LoggerMixin

# Локальні імпорти компонентів системи
from .function_definitions import FunctionDefinitions
from .function_executor import FunctionExecutor
from .model_manager import ModelManager
from .operations_manager import OperationsManager


class ChatAssistant(LoggerMixin):
    """
    Чат-асистент, який використовує трансформерну модель для обробки природної мови.

    Основні функції:
    - Інтерактивний чат з користувачем
    - Розпізнавання та виконання функцій
    - Управління історією розмови
    - Інтеграція з різними AI моделями
    """

    def __init__(self) -> None:
        """
        Ініціалізує чат-асистента з моделлю та необхідними компонентами.

        Створює:
        - ModelManager для роботи з AI моделями
        - OperationsManager для операцій з даними
        - FunctionExecutor для виконання функцій
        - Історію розмови
        """
        # Ініціалізуємо менеджер моделей (Singleton)
        self.model_manager = ModelManager()

        # Ініціалізуємо менеджер операцій для роботи з контактами та нотатками
        self.operations = OperationsManager()

        # Ініціалізуємо виконавець функцій
        self.function_executor = FunctionExecutor(self.operations)

        # Ініціалізуємо історію розмови (список обмінів між користувачем та асистентом)
        self.conversation_history: List[Dict[str, str]] = []
        self.is_running = True

        # Отримуємо системний промпт та доступні функції з відповідного класу
        self.system_prompt = FunctionDefinitions.SYSTEM_PROMPT
        self.available_functions = FunctionDefinitions.AVAILABLE_FUNCTIONS

    def welcome_message(self) -> str:
        """Повертає привітальне повідомлення для чат-асистента."""
        return "🤖 Welcome to CLI Assistant with AI!"

    def parse_function_call(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Парсить виклик функції з відповіді моделі.

        Підтримує різні формати викликів функцій:
        - OpenAI формат: "FUNCTION_CALL:function_name:arguments_json"
        - JSON в блоках коду: ```json {...} ```
        - Простий JSON: {...}

        Args:
            response: Відповідь моделі для парсингу

        Returns:
            Dict з деталями виклику функції або None якщо не знайдено
        """
        # Перевіряємо OpenAI формат виклику функції спочатку
        if response.startswith("FUNCTION_CALL:"):
            try:
                # Розділяємо на максимум 3 частини (префікс:функція:аргументи)
                parts = response.split(":", 2)
                if len(parts) >= 3:
                    function_name = parts[1]
                    arguments_json = parts[2]
                    arguments = json.loads(arguments_json)

                    # Створюємо об'єкт виклику функції
                    function_call = {
                        "function": function_name,
                        "arguments": arguments,
                        "tool_call_id": f"call_{function_name}_{hash(arguments_json) % 10000}",
                    }
                    print(f"🔍 Debug - Found OpenAI function call: {function_call}")
                    return function_call
            except (json.JSONDecodeError, IndexError) as e:
                print(f"🔍 Debug - Error parsing OpenAI function call: {e}")

        # Шукаємо JSON виклик функції в блоках коду
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                function_call = json.loads(json_match.group(1))
                # Додаємо tool_call_id якщо відсутній
                if "tool_call_id" not in function_call:
                    function_call["tool_call_id"] = (
                        f"call_{function_call.get('function', 'unknown')}_{hash(json_match.group(1)) % 10000}"
                    )
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(f"🔍 Debug - JSON decode error in code block: {e}")

        # Шукаємо JSON без блоків коду
        json_pattern = r'\{[^{}]*"function"[^{}]*\}'
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                function_call = json.loads(json_match.group(0))
                # Додаємо tool_call_id якщо відсутній
                if "tool_call_id" not in function_call:
                    function_call["tool_call_id"] = (
                        f"call_{function_call.get('function', 'unknown')}_{hash(json_match.group(0)) % 10000}"
                    )
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(f"🔍 Debug - JSON decode error without code block: {e}")

        # Шукаємо будь-яку JSON-подібну структуру
        json_pattern = r'\{.*?"function".*?\}'
        json_match = re.search(json_pattern, response, re.DOTALL)

        if json_match:
            try:
                # Намагаємось очистити JSON
                json_str = json_match.group(0)
                function_call = json.loads(json_str)
                # Додаємо tool_call_id якщо відсутній
                if "tool_call_id" not in function_call:
                    function_call["tool_call_id"] = (
                        f"call_{function_call.get('function', 'unknown')}_{hash(json_str) % 10000}"
                    )
                print(
                    f"\033[90m🔍 Debug - Found JSON-like structure: {function_call}\033[0m"
                )
                return function_call  # type: ignore[no-any-return]
            except json.JSONDecodeError as e:
                print(f"🔍 Debug - JSON decode error in JSON-like structure: {e}")

        # Виводимо debug повідомлення сірим кольором
        print(f"\033[90m🔍 Debug - No function call found in response\033[0m")
        return None

    def execute_function_call(
        self, function_call: Dict[str, Any], user_input: str
    ) -> str:
        """
        Виконує виклик функції використовуючи виконавець функцій.

        Args:
            function_call: Детали виклику функції
            user_input: Оригінальний запит користувача

        Returns:
            Результат виконання функції
        """
        return self.function_executor.execute_function_call(function_call, user_input)

    def generate_function_calling_response(self, user_input: str) -> str:
        """
        Генерує відповідь з можливістю виклику функцій.

        Процес:
        1. Підготовка повідомлень для моделі
        2. Генерація відповіді моделлю
        3. Парсинг можливих викликів функцій
        4. Виконання функцій за потреби

        Args:
            user_input: Запит користувача

        Returns:
            Відповідь асистента (текст або результат виконання функції)
        """
        try:
            # Підготовлюємо повідомлення використовуючи менеджер моделей
            messages = self.model_manager.prepare_messages(
                user_input, self.conversation_history
            )

            # Генеруємо відповідь використовуючи менеджер моделей
            assistant_response = self.model_manager.generate_function_calling_response(
                messages
            )

            # Намагаємось розпарсити виклик функції
            function_call = self.parse_function_call(assistant_response)

            if function_call:
                # Виконуємо функцію та отримуємо результат
                function_result = self.execute_function_call(function_call, user_input)

                # Додаємо повідомлення асистента з викликом функції до повідомлень
                assistant_tool_message = {
                    "role": "assistant",
                    "content": assistant_response,
                    "tool_calls": [
                        {
                            "id": function_call.get(
                                "tool_call_id", f"call_{function_call['function']}"
                            ),
                            "type": "function",
                            "function": {
                                "name": function_call["function"],
                                "arguments": json.dumps(function_call["arguments"]),
                            },
                        }
                    ],
                }

                # Створюємо копію повідомлень щоб не змінювати оригінал
                messages_copy = messages.copy()
                messages_copy.append(assistant_tool_message)  # type: ignore

                # Додаємо результат функції як tool повідомлення
                tool_message = {
                    "role": "tool",
                    "tool_call_id": function_call.get(
                        "tool_call_id", f"call_{function_call['function']}"
                    ),
                    "name": function_call["function"],
                    "content": function_result,
                }
                messages_copy.append(tool_message)  # type: ignore

                # Генеруємо фінальну відповідь на основі результату функції
                final_response = self.model_manager.generate_function_calling_response(
                    messages_copy
                )

                return final_response

            else:
                # Якщо немає виклику функції, перевіряємо команди за ключовими словами (запасний варіант)
                if "help" in user_input.lower() and (
                    "command" in assistant_response.lower()
                    or "help" in assistant_response.lower()
                ):
                    return FunctionDefinitions.HELP_MESSAGE

                # Повертаємо природну мовну відповідь асистента
                return assistant_response

        except Exception as e:
            self.logger.error(f"Error in function calling response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"

    def generate_response(self, user_input: str) -> str:
        """
        Генерує відповідь на основі введення користувача використовуючи AI.

        Основний метод для обробки запитів користувача:
        1. Перевіряє чи не пустий запит
        2. Обробляє команди виходу
        3. Передає запит функціональній моделі

        Args:
            user_input: Введення користувача

        Returns:
            Відповідь асистента
        """
        if not user_input.strip():
            return "I didn't catch that. Could you please say something?"

        # Перевіряємо команди виходу
        if any(cmd in user_input.lower() for cmd in ["exit", "quit", "bye", "goodbye"]):
            self.is_running = False
            return "Goodbye! Have a great day!"

        # Дозволяємо функціональній моделі обробити все
        response = self.generate_function_calling_response(user_input)

        return response

    def add_to_history(self, user_input: str, assistant_response: str) -> None:
        """
        Додає розмову до історії.

        Args:
            user_input: Запит користувача
            assistant_response: Відповідь асистента
        """
        self.conversation_history.append(
            {"user": user_input, "assistant": assistant_response}
        )

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Отримує історію розмови.

        Returns:
            Копія історії розмови
        """
        return self.conversation_history.copy()

    def chat_loop(self) -> None:
        """
        Основний цикл чату для інтерактивної розмови.

        Запускає безкінечний цикл взаємодії з користувачем:
        1. Виводить привітальне повідомлення
        2. Читає введення користувача
        3. Генерує та виводить відповідь
        4. Зберігає в історію
        5. Обробляє помилки та переривання
        """
        print(self.welcome_message())
        print("\n" + "=" * 50 + "\n")

        while self.is_running:
            try:
                # Читаємо введення користувача
                user_input = input("You: ").strip()

                # Пропускаємо пусті рядки
                if not user_input:
                    continue

                # Генеруємо відповідь
                response = self.generate_response(user_input)
                print(f"\nAssistant: {response}\n")

                # Додаємо до історії
                self.add_to_history(user_input, response)

                # Перевіряємо чи не треба завершити
                if not self.is_running:
                    break

            except KeyboardInterrupt:
                # Обробляємо Ctrl+C
                print("\n\nGoodbye! Thanks for chatting!")
                break
            except Exception as e:
                # Обробляємо інші помилки
                print(f"\nSorry, I encountered an error: {e}")
                print("Let's try again!\n")
