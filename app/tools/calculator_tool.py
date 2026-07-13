import ast
import operator
from typing import Dict, Any, Union

# Define supported operators
SUPPORTED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

def safe_eval(node: ast.AST) -> Union[int, float]:
    """
    Recursively evaluate an AST node safely, allowing only basic math operations.
    """
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
        
    elif isinstance(node, ast.Constant): # Python 3.8+ (covers Num)
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError(f"Unsupported constant type: {type(node.value).__name__}")
        
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op_type = type(node.op)
        
        if op_type not in SUPPORTED_OPERATORS:
            raise TypeError(f"Unsupported binary operator: {op_type.__name__}")
            
        # Handle division by zero
        if op_type == ast.Div and right == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        if op_type == ast.Mod and right == 0:
            raise ZeroDivisionError("Modulo by zero is not allowed.")
            
        # Prevent huge exponents to avoid hangs or memory issues (e.g. 9**9**9)
        if op_type == ast.Pow:
            if right > 1000 or left > 1000000:
                raise ValueError("Calculation exceeds allowed limits (exponent or base too large).")
                
        return SUPPORTED_OPERATORS[op_type](left, right)
        
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        op_type = type(node.op)
        
        if op_type not in SUPPORTED_OPERATORS:
            raise TypeError(f"Unsupported unary operator: {op_type.__name__}")
            
        return SUPPORTED_OPERATORS[op_type](operand)
        
    raise TypeError(f"Unsupported expression syntax: {type(node).__name__}")

def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate mathematical expressions.
    
    Args:
        expression: Mathematical expression string (e.g., "45000 * 18 / 100")
        
    Returns:
        A dictionary containing the expression and the result or error message.
    """
    if not expression or not isinstance(expression, str) or not expression.strip():
        return {
            "error": "Empty or invalid mathematical expression."
        }
        
    # Clean expression of potential format symbols (like commas in numbers e.g. 45,000 -> 45000)
    cleaned_expression = expression.replace(",", "").strip()
    
    try:
        # Parse expression into an AST (Abstract Syntax Tree)
        # Using ast.parse mode="eval" expects a single expression
        tree = ast.parse(cleaned_expression, mode="eval")
        result = safe_eval(tree)
        
        # Convert float to int if it's a whole number (e.g., 8100.0 -> 8100)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
            
        return {
            "expression": expression,
            "result": result
        }
    except ZeroDivisionError as e:
        return {
            "expression": expression,
            "error": str(e)
        }
    except (TypeError, ValueError) as e:
        return {
            "expression": expression,
            "error": f"Invalid expression or unsupported operation: {str(e)}"
        }
    except SyntaxError:
        return {
            "expression": expression,
            "error": "Syntax error in mathematical expression."
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": f"An unexpected error occurred during evaluation: {str(e)}"
        }
