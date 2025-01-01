let isError = false;

        // Function to update the current number display
        function appendNumber(number) {
            if (isError) clearDisplay();
            var currentNum = $("#number").html();
            var newNum = currentNum + number;
            $("#number").html(newNum);
        }

        // Function to append operators to the expression
        function appendOperator(operator) {
            var currentNum = $("#number").html();
            var expression = $("#expression").html();

            if (currentNum !== "") {
                expression += currentNum + " " + operator + " ";
                $("#expression").html(expression);
                $("#number").html('');
            }
        }

        // Function to evaluate the entire expression
        function evaluateExpression() {
            var expression = $("#expression").html() + $("#number").html();

            try {
                var result = customEval(expression);
                $("#expression").html(expression);
                $("#number").html("= " + result);
            } catch (error) {
                $("#number").html("Error");
                isError = true;
            }
        }

        // Handle keypress events for numbers, operators, and the equals key
        $(document).on('keypress', function (e) {
            var key = e.key;
            if (!isNaN(key)) {
                appendNumber(key);
            } else if (['+', '-', '*', '/', '.'].includes(key)) {
                appendOperator(key);
            } else if (key === '=' || key == 'Enter') {
                evaluateExpression();
            }
        });

        function clearDisplay() {
            $("#number").html('');
            $("#expression").html('');
            isError = false;
        }

        function removeLastCharacter() {
            var currentNum = $("#number").html();
            if (currentNum) {
                var updatedNum = currentNum.slice(0, -1);
                $("#number").html(updatedNum);
            }
        }

        // Button click events
        $('.calc-btn').on('click', function () {
            var key = $(this).data('event_key');

            if (['+', '-', '*', '/'].includes(key)) {
                appendOperator(key);
            }
            else if (key == ".") { appendDecimal(); }
            else if (key == '=' || key == 'Enter') {
                evaluateExpression();
            }
            else if (key === 'Backspace') {
                removeLastCharacter();
            }
            else if (key === 'Delete') {
                clearDisplay();
            }

            else {
                appendNumber(key);
            }
        });

        // Custom eval function to handle scientific operations
        function customEval(expression) {
            // Replace scientific functions with JavaScript equivalents
            expression = expression.replace(/sin\((.*?)\)/g, 'Math.sin($1)');
            expression = expression.replace(/cos\((.*?)\)/g, 'Math.cos($1)');
            expression = expression.replace(/tan\((.*?)\)/g, 'Math.tan($1)');
            expression = expression.replace(/log\((.*?)\)/g, 'Math.log10($1)');
            expression = expression.replace(/ln\((.*?)\)/g, 'Math.log($1)');
            expression = expression.replace(/sin⁻¹\((.*?)\)/g, 'Math.asin($1)');
            expression = expression.replace(/cos⁻¹\((.*?)\)/g, 'Math.acos($1)');
            expression = expression.replace(/tan⁻¹\((.*?)\)/g, 'Math.atan($1)');
            expression = expression.replace(/e/g, Math.E);
            expression = expression.replace(/π/g, Math.PI);
            expression = expression.replace(/√\((.*?)\)/g, 'Math.sqrt($1)');
            expression = expression.replace(/∛\((.*?)\)/g, 'Math.cbrt($1)');
            expression = expression.replace(/\^/g, 'Math.pow($1, $2)');
            expression = expression.replace(/10\^(\d+)/g, 'Math.pow(10, $1)');
            expression = expression.replace(/(\d+)!/g, 'factorial($1)');

            return eval(expression);  // Evaluate the expression
        }

        // Factorial function
        function factorial(n) {
            if (n == 0 || n == 1) return 1;
            return n * factorial(n - 1);
        }

        function appendDecimal() {
            var currentNum = $("#number").html();
            if (!currentNum.includes('.')) {
                $("#number").html(currentNum + '.');
            }
        }

        $(document).on('keydown', function () {
            if (isError) clearDisplay();
        });

        var isDegreeMode = true;

        $('.deg-rad-btn').on('click', function () {
            let selectedMode = $(this).text();

            if (selectedMode === 'Deg') {
                isDegreeMode = true;
                $('.deg-rad-btn[data-event_key="°"]').addClass('active');
                $('.deg-rad-btn[data-event_key="c"]').removeClass('active');
            }
            else if (selectedMode === 'Rad') {
                isDegreeMode = false;
                $('.deg-rad-btn[data-event_key="c"]').addClass('active');
                $('.deg-rad-btn[data-event_key="°"]').removeClass('active');
            }
        });

        function toggleDegreeRadian() {
            isDegreeMode = !isDegreeMode;
        }

        function toRadians(degrees) {
            return degrees * (Math.PI / 180);
        }

        function toDegrees(radians) {
            return radians * (180 / Math.PI);
        }

        function evaluateTrigFunction(fn, value) {
            if (isDegreeMode) {
                value = toRadians(value);
            }
            return evaluateScientificFunction(fn, value);
        }

        $('.deg-rad-btn').on('click', function () {
            toggleDegreeRadian();
            $(this).html(isDegreeMode ? "Deg" : "Rad");
        });
