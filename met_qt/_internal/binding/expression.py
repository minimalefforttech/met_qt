# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
import re
from weakref import proxy
from typing import Any, Dict, Callable
from met_qt._internal.qtcompat import QtCore

class ExpressionBinding:
    """
    Manages bindings from an expression with multiple variables to a target property.
    Allows for both format-string and eval-based expressions, with optional converters and math helpers.
    """
    
    def __init__(
        self,
        bindings_manager: QtCore.QObject,
        target: QtCore.QObject,
        target_property: str,
        expression_str: str,
        converter: Callable[[Any], Any] = None
    ) -> None:
        """
        Initialize an ExpressionBinding.
        Args:
            bindings_manager: The parent bindings manager.
            target: The target QObject.
            target_property: The property name on the target to update.
            expression_str: The expression string (format or eval).
            converter: Optional converter for the result.
        """
        self._bindings_manager = proxy(bindings_manager)
        self._target = target
        self._target_property = target_property
        self._expression_str = expression_str
        self._converter = converter
        self._variables = {}
        self._bindings = {}
        self._locals = {}
        self._use_eval = self._determine_if_use_eval(expression_str)
        self._updating = False
        self._building = False
        self._register_default_math_functions()
        
    def bind(
        self,
        var_name: str,
        obj: QtCore.QObject,
        property_name: str,
        converter: Callable[[Any], Any] = None
    ) -> 'ExpressionBinding':
        """
        Bind a variable in the expression to a property of an object.
        Args:
            var_name: The variable name in the expression.
            obj: The QObject to bind from.
            property_name: The property name on the object.
            converter: Optional converter for this variable.
        Returns:
            self
        """
        pattern = r'\b' + re.escape(var_name) + r'\b'
        if not re.search(pattern, self._expression_str):
            raise ValueError(f"Variable '{var_name}' not found in expression: {self._expression_str}")
        self._bindings[var_name] = (obj, property_name, converter)
        value = obj.property(property_name)
        value = self._convert_value(value, converter)
        self._variables[var_name] = value
        self._bindings_manager._connect_to_property_changes(
            obj, property_name, lambda: self._handle_property_change(var_name, obj, property_name))
        if not self._building:
            self._update_target()
        return self

    def _convert_value(self, value: Any, converter: Callable[[Any], Any] = None) -> Any:
        """
        Convert the value using the provided converter or, if in eval mode, attempt to convert to float/int as needed.
        Args:
            value: The value to convert.
            converter: Optional converter function.
        Returns:
            The converted value.
        """
        if converter is not None:
            return converter(value)
        elif self._use_eval:
            if value in (None, ""):
                return 0
            elif isinstance(value, str):
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
        return value
        
    def local(self, name: str, value: Any) -> 'ExpressionBinding':
        """
        Register a local value or function to be used in the expression.
        Args:
            name: The local variable/function name.
            value: The value or function.
        Returns:
            self
        """
        self._locals[name] = value
        if not self._building:
            self._update_target()
        return self
        
    def _register_default_math_functions(self) -> None:
        """
        Register default math helper functions for expressions (lerp, clamp, saturate).
        """
        self._locals.update({
            "lerp": lambda a, b, t: a + (b - a) * t,
            "clamp": lambda value, min_val, max_val: max(min(value, max_val), min_val),
            "saturate": lambda value: max(0, min(value, 1))
        })
        
    def _handle_property_change(self, var_name: str, obj: QtCore.QObject, property_name: str) -> None:
        """
        Handle property change events from bound variables.
        Args:
            var_name: The variable name in the expression.
            obj: The QObject whose property changed.
            property_name: The property name that changed.
        """
        if self._updating:
            return
        try:
            self._updating = True
            value = obj.property(property_name)
            _, _, converter = self._bindings[var_name]
            value = self._convert_value(value, converter)
            self._variables[var_name] = value
            self._update_target()
        finally:
            self._updating = False
        
    def _update_target(self) -> None:
        """
        Update the target property with the evaluated expression result.
        """
        try:
            result = self._evaluate_expression()
            if self._converter is not None:
                result = self._converter(result)
            elif self._use_eval:
                # If result is string and can be converted, do so
                if isinstance(result, str):
                    if result == "":
                        result = 0
                    elif '.' in result:
                        result = float(result)
                    else:
                        result = int(result)
            self._target.setProperty(self._target_property, result)
        except Exception as e:
            print(f"Expression failed: {self._target.metaObject().className()}.{self._target_property} = {self._expression_str} ({e})")
        
    def _evaluate_expression(self) -> Any:
        """
        Evaluate the expression using the current variable values.
        Returns:
            The result of the expression (type depends on expression and converter).
        """
        eval_env = self._create_eval_environment()
        if self._use_eval:
            return eval(self._expression_str, globals(), eval_env)
        else:
            result = self._expression_str
            pattern = r"{([^{}]*)}"
            matches = list(re.finditer(pattern, self._expression_str))
            for match in reversed(matches):
                expr = match.group(1)
                start, end = match.span()
                parts = expr.split(":")
                if len(parts) > 1:
                    var_name = parts[0].strip()
                    format_spec = parts[1].strip()
                    if var_name in eval_env:
                        value = eval_env[var_name]
                        formatted = format(value, format_spec)
                        result = result[:start] + formatted + result[end:]
                    else:
                        result = result[:start] + f"<unknown: {var_name}>" + result[end:]
                else:
                    try:
                        value = eval(expr, globals(), eval_env)
                        result = result[:start] + str(value) + result[end:]
                    except Exception as e:
                        result = result[:start] + f"<error:{e}>" + result[end:]
            return result
    
    def _create_eval_environment(self) -> Dict[str, Any]:
        """
        Create the environment dictionary for expression evaluation.
        Returns:
            A dictionary of variables and local helpers for eval/format.
        """
        env = {}
        env.update(self._variables)
        env.update(self._locals)
        
        if "lerp" not in env:
            env["lerp"] = lambda a, b, t: a + (b - a) * t
        if "clamp" not in env:
            env["clamp"] = lambda value, min_val, max_val: max(min(value, max_val), min_val)
        if "saturate" not in env:
            env["saturate"] = lambda value: max(0, min(value, 1))
            
        return env
    
    def _determine_if_use_eval(self, expression_str: str) -> bool:
        """
        Determine if the expression should be evaluated with eval (math/logic) or as a format string.
        Args:
            expression_str: The expression string.
        Returns:
            True if eval should be used, False for format string.
        """
        # Heuristic: if the expression is a single variable or contains math operators, use eval
        if any(op in expression_str for op in ['+', '-', '*', '/', '(', ')']):
            return True
        # If it's just a variable name
        if re.fullmatch(r"\w+", expression_str.strip()):
            return True
        return False
    
    def __enter__(self) -> 'ExpressionBinding':
        """
        Enter context for building the expression binding (batch variable binds).
        Returns:
            self
        """
        self._building = True
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Exit context for building the expression binding.
        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        Returns:
            False (do not suppress exceptions)
        """
        self._building = False
        return False
