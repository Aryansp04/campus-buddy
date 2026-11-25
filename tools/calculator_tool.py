import ast
import operator
import math
import re
from typing import Dict, Any, Union, List

# Allowed operators for safe AST evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
}

SAFE_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}

def _eval_node(node):
    """Safely evaluates an AST node."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division by zero")
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Operator not permitted: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](_eval_node(node.operand))
        raise ValueError(f"Unary operator not permitted: {op_type}")
    elif isinstance(node, ast.Name):
        if node.id in SAFE_CONSTANTS:
            return SAFE_CONSTANTS[node.id]
        raise ValueError(f"Undefined variable: '{node.id}'")
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCTIONS:
            args = [_eval_node(arg) for arg in node.args]
            return SAFE_FUNCTIONS[node.func.id](*args)
        raise ValueError("Function call not permitted")
    else:
        raise ValueError(f"Unsupported expression construct: {type(node).__name__}")

def safe_calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    """
    expr_clean = expression.strip().replace("^", "**")
    # Support natural "15% of 850" -> "(15/100) * 850"
    expr_clean = re.sub(r'(\d+(?:\.\d+)?)\s*%\s*of\s*', r'(\1/100) * ', expr_clean, flags=re.IGNORECASE)
    # Replace standalone percent e.g. "20% * 50" -> "(20/100) * 50"
    expr_clean = re.sub(r'(\d+(\.\d+)?)%', r'(\1/100)', expr_clean)

    try:
        parsed = ast.parse(expr_clean, mode="eval")
        result = _eval_node(parsed.body)
        
        # Round cleanly if float
        if isinstance(result, float):
            result = round(result, 6)
            if result.is_integer():
                result = int(result)

        return {
            "success": True,
            "expression": expression,
            "result": result,
            "formatted": f"{expression} = {result}"
        }
    except ZeroDivisionError:
        return {
            "success": False,
            "expression": expression,
            "error": "Error: Division by zero is undefined."
        }
    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": f"Invalid or unsupported mathematical expression."
        }

def calculate_attendance(attended: int, total: int, target_percent: float = 75.0) -> Dict[str, Any]:
    """
    Calculates attendance percentage and requirements for college compliance.
    """
    if total <= 0:
        return {
            "success": False,
            "error": "Total number of classes must be greater than zero."
        }
    if attended < 0 or attended > total:
        return {
            "success": False,
            "error": "Attended classes cannot be negative or exceed total classes."
        }

    current_percent = (attended / total) * 100.0
    status = "safe" if current_percent >= target_percent else "shortage"

    # Classes needed to reach target percentage:
    # (attended + x) / (total + x) >= target / 100
    # attended + x >= (target/100)*total + (target/100)*x
    # x * (1 - target/100) >= (target/100)*total - attended
    # x >= ((target/100)*total - attended) / (1 - target/100)
    target_frac = target_percent / 100.0
    if current_percent < target_percent:
        if target_frac >= 1.0:
            classes_needed = "Impossible (target is 100% and a class was missed)"
        else:
            diff = (target_frac * total - attended) / (1.0 - target_frac)
            classes_needed = max(0, math.ceil(diff))
        classes_can_miss = 0
    else:
        classes_needed = 0
        # Classes that can be missed:
        # attended / (total + y) >= target / 100
        # total + y <= attended / target_frac
        # y <= (attended / target_frac) - total
        diff = (attended / target_frac) - total
        classes_can_miss = max(0, math.floor(diff))

    summary = (
        f"📊 Attendance: {attended}/{total} classes ({current_percent:.2f}%).\n"
        f"🎯 Target: {target_percent}%."
    )
    if status == "shortage":
        summary += f"\n⚠️ Shortage! You must attend the next {classes_needed} class(es) consecutively to reach {target_percent}%."
    else:
        summary += f"\n✅ Safe! You are above the {target_percent}% requirement. You can safely miss up to {classes_can_miss} class(es) without falling below {target_percent}%."

    return {
        "success": True,
        "attended": attended,
        "total": total,
        "current_percentage": round(current_percent, 2),
        "target_percentage": target_percent,
        "status": status,
        "classes_needed_to_reach_target": classes_needed,
        "classes_can_miss": classes_can_miss,
        "summary": summary
    }

def calculate_gpa(courses: List[Dict[str, Union[float, int, str]]]) -> Dict[str, Any]:
    """
    Calculates GPA/SGPA based on grade points and course credits.
    Course dict: {"name": str, "credits": int/float, "grade_point": float}
    """
    if not courses:
        return {"success": False, "error": "No course grade information provided."}

    total_credits = 0.0
    weighted_points = 0.0

    grade_map = {
        "A+": 10.0, "O": 10.0,
        "A": 9.0,
        "B+": 8.0,
        "B": 7.0,
        "C+": 6.0,
        "C": 5.0,
        "D": 4.0,
        "F": 0.0
    }

    breakdown = []
    for c in courses:
        credits = float(c.get("credits", 3))
        gp = c.get("grade_point")
        if gp is None and "grade" in c:
            grade_str = str(c["grade"]).strip().upper()
            gp = grade_map.get(grade_str, 0.0)
        else:
            gp = float(gp if gp is not None else 0.0)

        total_credits += credits
        weighted_points += credits * gp
        breakdown.append({
            "course": c.get("name", "Course"),
            "credits": credits,
            "grade_point": gp,
            "weighted": round(credits * gp, 2)
        })

    if total_credits == 0:
        return {"success": False, "error": "Total credits cannot be zero."}

    gpa = round(weighted_points / total_credits, 2)
    return {
        "success": True,
        "gpa": gpa,
        "total_credits": total_credits,
        "weighted_points": round(weighted_points, 2),
        "breakdown": breakdown,
        "summary": f"🎓 Semester GPA / SGPA: {gpa:.2f} (Total Credits: {int(total_credits) if total_credits.is_integer() else total_credits})"
    }
