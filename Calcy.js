// toggle behavior: open/close the mobile menu
(function () {
    const toggle = document.getElementById('navToggle');
    const menu = document.getElementById('navMenu');

    toggle.addEventListener('click', function () {
        menu.classList.toggle('show');
    });

    // close menu when clicking outside
    document.addEventListener('click', function (e) {
        const target = e.target;
        if (!menu.contains(target) && !toggle.contains(target) && menu.classList.contains('show')) {
            menu.classList.remove('show');
        }
    });

    // close menu on Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && menu.classList.contains('show')) {
            menu.classList.remove('show');
        }
    });
})();

// --- State ---
let isError = false;
let isDegreeMode = true;

// --- Helpers to update UI ---
function setExpression(text) { $("#expression").text(text || ''); }
function setNumber(text) { $("#number").text(text || ''); }
function getExpression() { return $("#expression").text() || ''; }
function getNumber() { return $("#number").text() || ''; }

// Append raw token to the 'number' area (used for numbers and functions like sin( )
function appendNumber(token) {
    if (isError) { clearDisplay(); }
    $("#number").text(getNumber() + token);
}

// When operator clicked, push current number to expression and add operator
function appendOperator(op) {
    let cur = getNumber();
    let expr = getExpression();

    // If number area empty and expression ends with an operator, allow replacing
    if (!cur && expr && /[+\-*/^ ]$/.test(expr)) {
        expr = expr.slice(0, -1) + op;
        setExpression(expr);
        return;
    }

    if (cur === '' && expr === '' && (op === '+' || op === '-')) {
        // allow unary + or - in number zone
        appendNumber(op);
        return;
    }

    if (cur !== '') {
        // If we are adding an operator but number ends with '(' (e.g. user pressed function)
        // we allow adding directly: e.g. sin( -> treat as part of number, avoid adding operator
        setExpression(expr + cur + op);
        setNumber('');
    } else {
        // if no current number, append op to expression
        setExpression(expr + op);
    }
}

function clearDisplay() {
    setNumber('');
    setExpression('');
    isError = false;
}

function removeLastCharacter() {
    let cur = getNumber();
    if (cur && cur.length > 0) {
        setNumber(cur.slice(0, -1));
    } else {
        // if number empty, remove last char from expression
        let e = getExpression();
        setExpression(e.slice(0, -1));
    }
}

// --- Backend communication ---
async function evaluateExpression() {
    let expression = getExpression() + getNumber();
    if (!expression) return;
    try {
        const resp = await fetch("http://127.0.0.1:5000/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ expression: expression })
        });
        const data = await resp.json();
        // show original expression on top and result in number with leading "="
        setExpression(expression);
        setNumber("= " + data.result);
    } catch (err) {
        setNumber("Error");
        isError = true;
        console.error(err);
    }
}

// Toggle degree/radian mode both UI and backend
async function switchMode(mode) {
    if (mode === 'toggle') {
        isDegreeMode = !isDegreeMode;
    } else {
        isDegreeMode = (mode === 'deg');
    }
    $("#modeToggle").text(isDegreeMode ? 'Deg' : 'Rad');
    // notify backend
    try {
        await fetch("http://127.0.0.1:5000/mode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode: isDegreeMode ? 'deg' : 'rad' })
        });
    } catch (e) { console.warn('mode sync failed'); }
}

// --- Event handling for buttons ---
$(document).ready(function () {
    // Button clicks
    $('.btn-key').on('click', function () {
        const key = $(this).data('event_key');

        if (['+', '-', '*', '/', '^', ' * 10^', '×', '÷'].includes(key)) {
            // normalize the ×10^ special key
            if (key === ' * 10^' || key === '×10^') {
                appendNumber(' * 10^');
            } else {
                appendOperator(key);
            }
        } else if (key === '=') {
            evaluateExpression();
        } else if (key === 'Backspace') {
            removeLastCharacter();
        } else if (key === 'Delete') {
            clearDisplay();
        } else if (key === '°') { // keep compatibility; in grid we used mode toggle button
            switchMode('deg');
        } else if (key === 'c') {
            switchMode('rad');
        } else if (key === 'e') {
            appendNumber('e');
        } else {
            appendNumber(key);
        }
    });

    // Mode toggle top-right
    $('#modeToggle').on('click', function () { switchMode('toggle'); });

    // Keyboard handling (keydown to catch backspace/delete)
    $(document).on('keydown', function (e) {
        const key = e.key;

        // allow numbers and parentheses and decimal
        if ((key >= '0' && key <= '9') || key === '.') {
            appendNumber(key);
            e.preventDefault();
            return;
        }

        // functions mapped to single-letter shortcuts (optional)
        // s -> sin(, o -> cos(, t -> tan(, l -> ln(, g -> log(
        if (key.toLowerCase() === 's') { appendNumber('sin('); e.preventDefault(); return; }
        if (key.toLowerCase() === 'o') { appendNumber('cos('); e.preventDefault(); return; }
        if (key.toLowerCase() === 't') { appendNumber('tan('); e.preventDefault(); return; }
        if (key.toLowerCase() === 'l') { appendNumber('ln('); e.preventDefault(); return; }
        if (key.toLowerCase() === 'g') { appendNumber('log('); e.preventDefault(); return; }

        if (['+', '-', '*', '/', '^', '%'].includes(key)) {
            appendOperator(key);
            e.preventDefault();
            return;
        }

        if (key === 'Enter' || key === '=') {
            evaluateExpression();
            e.preventDefault();
            return;
        }

        if (key === 'Backspace') {
            removeLastCharacter();
            e.preventDefault();
            return;
        }

        if (key === 'Delete' || key === 'Escape') {
            clearDisplay();
            e.preventDefault();
            return;
        }

        if (key === '(' || key === ')') {
            appendNumber(key);
            e.preventDefault();
            return;
        }

        // quick inserts
        if (key.toLowerCase() === 'p') { appendNumber('π'); e.preventDefault(); return; }
        if (key.toLowerCase() === 'e') { appendNumber('e'); e.preventDefault(); return; }
    });

    // Nice UX: copy result by clicking the result
    $('#number').on('click', function () {
        const txt = $(this).text();
        if (txt.startsWith('= ')) {
            const toCopy = txt.slice(2);
            navigator.clipboard?.writeText(toCopy).then(() => {
                // subtle feedback
                $(this).fadeOut(100).fadeIn(100);
            });
        }
    });
});

