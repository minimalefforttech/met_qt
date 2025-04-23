# copyright (c) 2025 Alex Telford, http://minimaleffort.tech
import re
from weakref import proxy
from typing import Any, Dict, Callable
from met_qt._internal.qtcompat import QtCore

class ExpressionBinding:
    """Manages bindings from an expression with multiple variables to a target property"""
    
    def __init__(self, bindings_manager, target, target_property, expression_str, converter=None):
        self._bindings_manager = proxy(bindings_manager)
        self._target = target
        self._target_property = target_property
        self._expression_str = expression_str
        self._converter = converter
        self._variables = {}
        self._bindings = {}
        self._locals = {}
        self._is_string_output = self._determine_if_string_output(target, target_property, converter)
        self._updating = False
        self._register_default_math_functions()
        
    def bind(self, var_name: str, obj: QtCore.QObject, property_name: str) -> 'ExpressionBinding':
        """Bind a variable in the expression to a property of an object"""
        pattern = r'\b' + re.escape(var_name) + r'\b'
        if not re.search(pattern, self._expression_str):
            raise ValueError(f"Variable '{var_name}' not found in expression: {self._expression_str}")
        
        self._bindings[var_name] = (obj, property_name)
        self._variables[var_name] = obj.property(property_name)
        self._bindings_manager._connect_to_property_changes(
            obj, property_name, lambda: self._handle_property_change(var_name, obj, property_name))
        self._update_target()
        return self
        
    def local(self, name: str, value: Any) -> 'ExpressionBinding':
        """Register a local value or function to be used in the expression"""
        self._locals[name] = value
        self._update_target()
        return self
        
    def _register_default_math_functions(self):
        """Register default math helper functions for expressions"""
        self._locals.update({
            "lerp": lambda a, b, t: a + (b - a) * t,
            "clamp": lambda value, min_val, max_val: max(min(value, max_val), min_val),
            "saturate": lambda value: max(0, min(value, 1))
        })
        
    def _handle_property_change(self, var_name: str, obj: QtCore.QObject, property_name: str):
        """Handle property change events from bound variables"""
        if self._updating:
            return
            
        try:
            self._updating = True
            self._variables[var_name] = obj.property(property_name)
            self._update_target()
        finally:
            self._updating = False
        
    def _update_target(self):
        """Update the target property with the evaluated expression result"""
        try:
            result = self._evaluate_expression()
            if self._converter:
                result = self._converter(result)
            self._target.setProperty(self._target_property, result)
        except Exception as e:
            import traceback
            traceback.print_exc()
        
    def _evaluate_expression(self) -> Any:
        """Evaluate the expression using the current variable values"""
        eval_env = self._create_eval_environment()
            
        if self._is_string_output:
            try:
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
            except Exception as e:
                return f"<formatting error: {str(e)}>"
        else:
            try:
                result = eval(self._expression_str, globals(), eval_env)
                return result
            except Exception:
                return 0
            
    def _create_eval_environment(self) -> Dict[str, Any]:
        """Create the environment dictionary for expression evaluation"""
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
    
    def _determine_if_string_output(self, target: QtCore.QObject, target_property: str, 
                                  converter: Callable = None) -> bool:
        """Determine if the expression should output a string value"""
        if converter is not None:
            try:
                result = converter("test")
                return isinstance(result, str)
            except:
                pass
        
        if "{" in self._expression_str and "}" in self._expression_str:
            return True
            
        meta_obj = target.metaObject()
        property_index = meta_obj.indexOfProperty(target_property)
        
        if property_index >= 0:
            meta_property = meta_obj.property(property_index)
            property_type = meta_property.typeName()
            
            if property_type in ["QString", "QByteArray", "QChar", "char*"]:
                return True
                
            current_value = target.property(target_property)
            return isinstance(current_value, str)
            
        return False
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
