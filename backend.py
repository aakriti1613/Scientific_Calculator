from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from sympy.integrals.manualintegrate import integral_steps
from sympy.integrals.transforms import (
    laplace_transform,
    inverse_laplace_transform,
    fourier_transform,
    inverse_fourier_transform,
)

app = Flask(__name__)
CORS(app)

DEG_MODE = True

TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)

COMMON_SYMBOLS = {
    "pi": sp.pi,
    "PI": sp.pi,
    "e": sp.E,
    "E": sp.E,
    "i": sp.I,
    "I": sp.I,
    "oo": sp.oo,
    "inf": sp.oo,
    "-oo": -sp.oo,
    "-inf": -sp.oo,
}

SYMPY_FUNCTIONS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "cot": sp.cot,
    "sec": sp.sec,
    "csc": sp.csc,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "atan2": sp.atan2,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "coth": sp.coth,
    "asinh": sp.asinh,
    "acosh": sp.acosh,
    "atanh": sp.atanh,
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "sqrt": sp.sqrt,
    "Abs": sp.Abs,
    "sign": sp.sign,
    "gamma": sp.gamma,
    "Gamma": sp.gamma,
    "factorial": sp.factorial,
    "floor": sp.floor,
    "ceiling": sp.ceiling,
    "Heaviside": sp.Heaviside,
    "DiracDelta": sp.DiracDelta,
    "erf": sp.erf,
    "cbrt": lambda arg: sp.real_root(arg, 3),
    "Integer": sp.Integer,
    "Rational": sp.Rational,
    "Float": sp.Float,
    "Symbol": sp.Symbol,
    "Pow": sp.Pow,
}

PARSE_GLOBALS = {**COMMON_SYMBOLS, **SYMPY_FUNCTIONS}


def switch_mode(mode: str) -> str:
    global DEG_MODE
    if mode.lower() == "deg":
        DEG_MODE = True
    elif mode.lower() == "rad":
        DEG_MODE = False
    return f"Mode set to {'Degrees' if DEG_MODE else 'Radians'}"


def sanitize_expression(expr: str) -> str:
    if expr is None:
        return ""
    replacements = {
        "√": "sqrt",
        "∛": "cbrt",
        "÷": "/",
        "×": "*",
        "^": "**",
        "–": "-",
        "−": "-",
    }
    sanitized = str(expr)
    for src, dest in replacements.items():
        sanitized = sanitized.replace(src, dest)
    return sanitized


def parse_sympy_expression(expr_str, local_symbols=None):
    if isinstance(expr_str, (int, float)):
        return sp.nsimplify(expr_str)

    if local_symbols is None:
        local_symbols = {}

    sanitized = sanitize_expression(expr_str)
    local_dict = {**PARSE_GLOBALS, **local_symbols}

    try:
        return parse_expr(
            sanitized,
            transformations=TRANSFORMATIONS,
            local_dict=local_dict,
            global_dict=local_dict,
            evaluate=True,
        )
    except Exception as exc:
        raise ValueError(f"Unable to parse expression '{expr_str}': {exc}")


def parse_optional_value(value, local_symbols):
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in {"", "none", "null"}:
        return None
    return parse_sympy_expression(value, local_symbols)


def pack_expr(expr):
    if isinstance(expr, sp.Basic):
        return {"str": sp.sstr(expr), "latex": sp.latex(expr)}
    if isinstance(expr, (list, tuple)):
        return [pack_expr(item) for item in expr]
    if isinstance(expr, dict):
        return {key: pack_expr(val) for key, val in expr.items()}
    return expr


def pack_numeric(expr, precision=12):
    try:
        numeric = sp.N(expr, precision)
        return str(numeric)
    except Exception:
        return None


def compute_alternate_forms(expr, symbol=None):
    forms = []

    try:
        simplified = sp.simplify(expr)
        if simplified != expr:
            forms.append({"label": "Simplified", "expression": pack_expr(simplified)})
    except Exception:
        pass

    try:
        expanded = sp.expand(expr)
        if expanded != expr:
            forms.append({"label": "Expanded", "expression": pack_expr(expanded)})
    except Exception:
        pass

    try:
        factored = sp.factor(expr)
        if factored != expr:
            forms.append({"label": "Factored", "expression": pack_expr(factored)})
    except Exception:
        pass

    if symbol is not None:
        try:
            partial = sp.apart(expr, symbol)
            if partial != expr:
                forms.append({"label": "Partial fractions", "expression": pack_expr(partial)})
        except Exception:
            pass

    return forms


def describe_manual_integral_steps(expr, symbol, limit=60):
    try:
        root = integral_steps(expr, symbol)
    except Exception:
        return []

    steps = []
    visited = 0

    def visit(step):
        nonlocal visited
        if step is None or visited >= limit:
            return
        visited += 1

        cls = step.__class__.__name__

        if cls == "AlternativeRule":
            steps.append(
                f"Consider alternative methods for the integral of {sp.sstr(step.integrand)} with respect to {step.variable}."
            )
            for index, alt in enumerate(step.alternatives, start=1):
                steps.append(f"Alternative {index}: apply {alt.__class__.__name__}.")
                visit(alt)
        elif cls == "URule":
            steps.append(
                f"Use substitution u = {sp.sstr(step.u_func)}; du = {sp.sstr(sp.diff(step.u_func, step.variable))} d{step.variable}."
            )
            visit(step.substep)
        elif cls == "ConstantTimesRule":
            steps.append(f"Factor constant {sp.sstr(step.constant)} outside the integral.")
            visit(step.substep)
        elif cls == "AddRule":
            steps.append("Split the integral across additive terms.")
            for sub in step.substeps:
                visit(sub)
        elif cls == "PartsRule":
            steps.append(f"Integration by parts with u = {sp.sstr(step.u)} and dv = {sp.sstr(step.dv)}.")
            v_step = getattr(step, "v_step", None)
            if v_step is not None:
                steps.append("Integrate dv to obtain v.")
                visit(v_step)
            second = getattr(step, "second_step", None)
            if second is not None:
                steps.append("Integrate the remaining factor.")
                visit(second)
        elif cls == "PowerRule":
            steps.append("Apply the power rule for integrals.")
            sub = getattr(step, "substep", None)
            if sub is not None:
                visit(sub)
        elif cls == "ExpRule":
            steps.append("Integrate exponential function.")
        elif cls == "SinRule":
            steps.append("Integrate sine: integral of sin(u) du equals -cos(u) + C.")
        elif cls == "CosRule":
            steps.append("Integrate cosine: integral of cos(u) du equals sin(u) + C.")
        elif cls == "TanRule":
            steps.append("Integrate tangent: integral of tan(u) du equals -ln|cos(u)| + C.")
        elif cls == "CotRule":
            steps.append("Integrate cotangent: integral of cot(u) du equals ln|sin(u)| + C.")
        elif cls == "SecRule":
            steps.append("Integrate secant: integral of sec(u) du equals ln|sec(u)+tan(u)| + C.")
        elif cls == "CscRule":
            steps.append("Integrate cosecant: integral of csc(u) du equals -ln|csc(u)+cot(u)| + C.")
        elif cls == "SinhRule":
            steps.append("Integrate hyperbolic sine function.")
        elif cls == "CoshRule":
            steps.append("Integrate hyperbolic cosine function.")
        elif cls == "TanhRule":
            steps.append("Integrate hyperbolic tangent function.")
        else:
            substep = getattr(step, "substep", None)
            substeps = getattr(step, "substeps", None)
            if substep is not None:
                steps.append(f"Apply {cls}.")
                visit(substep)
            elif substeps is not None:
                steps.append(f"Apply {cls} across substeps.")
                for sub in substeps:
                    visit(sub)
            else:
                steps.append(f"Apply {cls} technique.")

    visit(root)

    cleaned = []
    for line in steps:
        if line and (not cleaned or cleaned[-1] != line):
            cleaned.append(line)
    return cleaned


def generate_limit_samples(expr, symbol, point, direction, sample_count=3):
    samples = []

    def evaluate_at(value):
        try:
            return str(sp.N(expr.subs(symbol, value)))
        except Exception:
            return None

    if point in (sp.oo, -sp.oo):
        seeds = [10 ** k for k in range(1, sample_count + 1)]
        for seed in seeds:
            val = seed if point == sp.oo else -seed
            numeric = evaluate_at(val)
            if numeric is not None:
                samples.append({"point": str(val), "value": numeric})
        return samples

    try:
        base_point = sp.N(point)
    except Exception:
        base_point = point

    deltas = [sp.Rational(1, 10 ** k) for k in range(1, sample_count + 1)]

    if direction == "+":
        dirs = ["+"]
    elif direction == "-":
        dirs = ["-"]
    else:
        dirs = ["-", "+"]

    for sign in dirs:
        for delta in deltas:
            value = point + delta if sign == "+" else point - delta
            numeric = evaluate_at(value)
            if numeric is not None:
                samples.append({"point": str(sp.N(value)), "value": numeric})

    return samples


def handle_integral(data):
    expression = data.get("expression", "")
    variables_spec = data.get("variables") or []

    if not variables_spec:
        symbol_name = data.get("var") or data.get("variable") or "x"
        variables_spec = [
            {
                "symbol": symbol_name,
                "lower": data.get("lower"),
                "upper": data.get("upper"),
            }
        ]

    var_symbols = {}
    for spec in variables_spec:
        name = spec.get("symbol") or "x"
        if name not in var_symbols:
            var_symbols[name] = sp.Symbol(name)

    expr = parse_sympy_expression(expression, var_symbols)

    integration_args = []
    definite = False
    for spec in variables_spec:
        name = spec.get("symbol") or "x"
        symbol = var_symbols[name]
        lower = parse_optional_value(spec.get("lower"), var_symbols)
        upper = parse_optional_value(spec.get("upper"), var_symbols)
        if lower is not None and upper is not None:
            integration_args.append((symbol, lower, upper))
            definite = True
        else:
            integration_args.append(symbol)

    try:
        result = sp.integrate(expr, *integration_args)
    except Exception as exc:
        raise ValueError(f"SymPy could not integrate the expression: {exc}")

    settings = data.get("settings", {})
    response = {
        "result": pack_expr(result),
        "input_simplified": pack_expr(sp.simplify(expr)),
    }

    needs_steps = settings.get("steps") and len(integration_args) == 1 and not isinstance(integration_args[0], tuple)
    if needs_steps:
        steps = describe_manual_integral_steps(expr, integration_args[0])
        if steps:
            response["steps"] = steps

    if settings.get("alternate_forms"):
        primary_symbol = next(iter(var_symbols.values())) if var_symbols else None
        response["alternate_forms"] = compute_alternate_forms(result, symbol=primary_symbol)

    if settings.get("numeric") and definite:
        response["numeric"] = pack_numeric(result)

    if not definite:
        response["constant_of_integration"] = "C"

    response["metadata"] = {
        "variables": [spec.get("symbol") or "x" for spec in variables_spec],
        "definite": definite,
    }

    return response


def handle_derivative(data):
    expression = data.get("expression", "")
    variables_spec = data.get("variables") or []

    if not variables_spec:
        symbol_name = data.get("var") or data.get("variable") or "x"
        variables_spec = [{"symbol": symbol_name, "order": data.get("order", 1)}]

    var_symbols = {}
    for spec in variables_spec:
        name = spec.get("symbol") or "x"
        if name not in var_symbols:
            var_symbols[name] = sp.Symbol(name)

    expr = parse_sympy_expression(expression, var_symbols)
    result = expr
    summary = []

    for spec in variables_spec:
        name = spec.get("symbol") or "x"
        order = spec.get("order", 1)
        try:
            order = int(order)
        except Exception:
            order = 1
        order = max(order, 1)
        result = sp.diff(result, var_symbols[name], order)
        summary.append({"variable": name, "order": order})

    settings = data.get("settings", {})
    response = {
        "result": pack_expr(result),
        "input_simplified": pack_expr(sp.simplify(expr)),
        "metadata": {"orders": summary},
    }

    if settings.get("alternate_forms"):
        response["alternate_forms"] = compute_alternate_forms(result)

    return response


def handle_limit(data):
    expression = data.get("expression", "")
    variable = data.get("variable") or data.get("var") or "x"
    direction = data.get("direction", "two-sided")
    point_raw = data.get("point", 0)

    symbol = sp.Symbol(variable)
    expr = parse_sympy_expression(expression, {variable: symbol})
    point = parse_optional_value(point_raw, {variable: symbol})
    if point is None:
        point = 0

    limit_kwargs = {}
    if direction in {"+", "-"}:
        limit_kwargs["dir"] = direction

    try:
        result = sp.limit(expr, symbol, point, **limit_kwargs)
    except Exception as exc:
        raise ValueError(f"Unable to compute limit: {exc}")

    settings = data.get("settings", {})
    response = {
        "result": pack_expr(result),
        "input_simplified": pack_expr(sp.simplify(expr)),
        "metadata": {"direction": direction, "point": pack_expr(point)},
    }

    if settings.get("numeric"):
        response["numeric"] = pack_numeric(result)
        response["samples"] = generate_limit_samples(expr, symbol, point, direction)

    return response


def handle_series(data):
    expression = data.get("expression", "")
    variable = data.get("variable") or data.get("var") or "x"
    point_raw = data.get("point", 0)
    order = data.get("order", 6)
    settings = data.get("settings", {})

    try:
        order = int(order)
    except Exception:
        order = 6
    order = max(order, 1)

    symbol = sp.Symbol(variable)
    expr = parse_sympy_expression(expression, {variable: symbol})
    point = parse_optional_value(point_raw, {variable: symbol})
    if point is None:
        point = 0

    try:
        series = sp.series(expr, symbol, point, order)
    except Exception as exc:
        raise ValueError(f"Unable to compute series expansion: {exc}")

    truncated = series.removeO()
    include_big_o = bool(settings.get("include_big_o", True))

    response = {
        "result": pack_expr(series if include_big_o else truncated),
        "expanded": pack_expr(truncated),
        "input_simplified": pack_expr(sp.simplify(expr)),
        "metadata": {"order": order, "point": pack_expr(point)},
    }

    if include_big_o:
        response["big_o"] = str(series.getO())

    coefficients = []
    try:
        expanded_terms = sp.expand(truncated).as_ordered_terms()
        for term in expanded_terms:
            coeff, exponent = term.as_coeff_exponent(symbol)
            coefficients.append({
                "power": int(exponent),
                "coefficient": pack_expr(coeff),
            })
    except Exception:
        coefficients = []

    if coefficients:
        response["coefficients"] = coefficients

    return response


def handle_transform(data):
    operation = data.get("operation")
    expression = data.get("expression", "")
    source_name = data.get("variable") or data.get("source") or "t"
    target_name = data.get("target") or ("s" if "laplace" in operation else "w")

    source = sp.Symbol(source_name)
    target = sp.Symbol(target_name)
    expr = parse_sympy_expression(expression, {source_name: source})

    if operation == "laplace":
        try:
            result, convergence, condition = laplace_transform(expr, source, target)
        except Exception as exc:
            raise ValueError(f"Laplace transform failed: {exc}")
        response = {
            "result": pack_expr(result),
            "metadata": {
                "convergence": str(convergence),
                "conditions": str(condition),
            },
        }
    elif operation == "inverse_laplace":
        try:
            result = inverse_laplace_transform(expr, source, target)
        except Exception as exc:
            raise ValueError(f"Inverse Laplace transform failed: {exc}")
        response = {"result": pack_expr(result)}
    elif operation == "fourier":
        try:
            result = fourier_transform(expr, source, target)
        except Exception as exc:
            raise ValueError(f"Fourier transform failed: {exc}")
        response = {"result": pack_expr(result)}
    elif operation == "inverse_fourier":
        try:
            result = inverse_fourier_transform(expr, source, target)
        except Exception as exc:
            raise ValueError(f"Inverse Fourier transform failed: {exc}")
        response = {"result": pack_expr(result)}
    else:
        raise ValueError(f"Unsupported transform operation '{operation}'")

    response["input_simplified"] = pack_expr(sp.simplify(expr))
    response["metadata"] = {
        **response.get("metadata", {}),
        "source": source_name,
        "target": target_name,
    }
    return response


def handle_algebraic_tools(data):
    expression = data.get("expression", "")
    variable = data.get("variable") or data.get("var") or "x"
    operations = data.get("settings", {}).get("operations") or ["simplify"]

    symbol = sp.Symbol(variable)
    expr = parse_sympy_expression(expression, {variable: symbol})

    seen = set()
    results = []

    for op in operations:
        if not op:
            continue
        if op in seen:
            continue
        seen.add(op)

        try:
            if op == "simplify":
                transformed = sp.simplify(expr)
            elif op == "expand":
                transformed = sp.expand(expr)
            elif op == "factor":
                transformed = sp.factor(expr)
            elif op == "apart":
                transformed = sp.apart(expr, symbol)
            elif op == "rewrite_trig":
                transformed = sp.simplify(expr.rewrite(sp.sin))
            elif op == "rewrite_exp":
                transformed = sp.simplify(expr.rewrite(sp.exp))
            else:
                results.append({"label": op, "error": "Unknown tool"})
                continue

            results.append({
                "label": op.replace("_", " ").title(),
                "expression": pack_expr(transformed),
            })
        except Exception as exc:
            results.append({"label": op, "error": str(exc)})

    return {
        "result": pack_expr(expr),
        "alternate_forms": results,
    }


@app.route("/calculus", methods=["POST"])
def calculus():
    data = request.get_json(silent=True) or {}
    operation = (data.get("operation") or "").lower()

    try:
        if operation in {"integrate", "integral"}:
            payload = handle_integral(data)
        elif operation in {"differentiate", "derivative"}:
            payload = handle_derivative(data)
        elif operation == "limit":
            payload = handle_limit(data)
        elif operation == "series":
            payload = handle_series(data)
        elif operation in {"laplace", "inverse_laplace", "fourier", "inverse_fourier"}:
            payload = handle_transform(data)
        elif operation == "algebraic_tools":
            payload = handle_algebraic_tools(data)
        else:
            return jsonify({"error": f"Unsupported operation '{operation}'"}), 400

        payload["operation"] = operation
        return jsonify(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Unexpected error: {exc}"}), 500


def fix_expression(expr):
    expr = sanitize_expression(expr)
    expr = re.sub(r"(\d)([a-zA-Zπe\(])", r"\1*\2", expr)
    expr = re.sub(r"(\))(\d)", r"\1*\2", expr)
    expr = re.sub(r"(\))([a-zA-Zπe\(])", r"\1*\2", expr)
    expr = re.sub(r"(\d+(\.\d+)?)%(?!\d)", r"(\1/100)", expr)
    expr = re.sub(r"(\d+)!", r"math.factorial(\1)", expr)
    return expr


def eval_expression(expr: str):
    open_brackets = expr.count("(")
    close_brackets = expr.count(")")
    if open_brackets > close_brackets:
        expr += ")" * (open_brackets - close_brackets)

    expr = fix_expression(expr)
    expr = expr.replace("π", "math.pi").replace("e", "math.e")
    expr = expr.replace("√", "math.sqrt").replace("∛", "math.pow")
    expr = expr.replace("^", "**").replace("×", "*").replace("÷", "/")
    expr = re.sub(r"×10\^(\d+)", r"*10**\1", expr)
    expr = re.sub(r"math\.pow\(([^)]+)\)", r"math.pow(\1, 1/3)", expr)

    if DEG_MODE:
        expr = re.sub(r"sin\(([^)]+)\)", r"math.sin(math.radians(\1))", expr)
        expr = re.sub(r"cos\(([^)]+)\)", r"math.cos(math.radians(\1))", expr)
        expr = re.sub(r"tan\(([^)]+)\)", r"math.tan(math.radians(\1))", expr)
        expr = re.sub(r"sin⁻¹\(([^)]+)\)", r"math.degrees(math.asin(\1))", expr)
        expr = re.sub(r"cos⁻¹\(([^)]+)\)", r"math.degrees(math.acos(\1))", expr)
        expr = re.sub(r"tan⁻¹\(([^)]+)\)", r"math.degrees(math.atan(\1))", expr)
    else:
        expr = re.sub(r"sin\(([^)]+)\)", r"math.sin(\1)", expr)
        expr = re.sub(r"cos\(([^)]+)\)", r"math.cos(\1)", expr)
        expr = re.sub(r"tan\(([^)]+)\)", r"math.tan(\1)", expr)
        expr = re.sub(r"sin⁻¹\(([^)]+)\)", r"math.asin(\1)", expr)
        expr = re.sub(r"cos⁻¹\(([^)]+)\)", r"math.acos(\1)", expr)
        expr = re.sub(r"tan⁻¹\(([^)]+)\)", r"math.atan(\1)", expr)

    expr = expr.replace("log", "math.log10").replace("ln", "math.log")
    expr = re.sub(r"sinh\(([^)]+)\)", r"math.sinh(\1)", expr)
    expr = re.sub(r"cosh\(([^)]+)\)", r"math.cosh(\1)", expr)

    try:
        return eval(expr, {"__builtins__": None}, {"math": math})
    except Exception:
        return "Error"


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json or {}
    expr = data.get("expression", "")
    result = eval_expression(expr)
    return jsonify({"result": result})


@app.route("/mode", methods=["POST"])
def mode():
    data = request.json or {}
    chosen = data.get("mode", "deg")
    message = switch_mode(chosen)
    return jsonify({"message": message})


if __name__ == "__main__":
    app.run(debug=True)