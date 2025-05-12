import math

class CalculatorService:
    def calculate(self, expression: str) -> str:
        """Вычисляет математическое выражение с проверкой безопасности"""
        try:
            # Разрешенные функции и константы
            allowed_names = {
                k: v for k, v in math.__dict__.items() 
                if not k.startswith("_")
            }
            allowed_names.update({
                'abs': abs,
                'round': round,
                'min': min,
                'max': max
            })
            
            # Проверка безопасности выражения
            code = compile(expression, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    return f"Ошибка: использование '{name}' запрещено"
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"Результат: {result}"
        except Exception as e:
            return f"Ошибка вычисления: {str(e)}"