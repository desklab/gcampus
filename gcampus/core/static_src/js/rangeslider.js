    (function () {


        var parent = document.querySelector(".range-slider");
        if (!parent) return;

        var
            rangeS = parent.querySelectorAll("input[type=range]"),
            numberS = parent.querySelectorAll("input[type=date]");

        // Set start and endpoint to first and last entry of week_list_js
        var left_slider_index = 0;
        var right_slider_index = week_list_length;

        // Check if there is already a set value in the hidden inputs
        // This means that the filter has been used and the slider as well
        // as the strings need to be set accordingly
        if (numberS[0].value && numberS[1].value ) {

            // Get values from hidden inputs
            var left_slider_date = Date.parse(numberS[0].value);
            var right_slider_date = Date.parse(numberS[1].value);

            // Get index of closest date in week_list_js
            left_slider_index = closest_index(left_slider_date, week_list_js);
            right_slider_index = closest_index(right_slider_date, week_list_js);

            // Set slider values
            rangeS[0].value = left_slider_index;
            rangeS[1].value = right_slider_index;
        }
        // Turn milliseconds into dates
        var start_date = new Date(week_list_js[left_slider_index]);
        var end_date = new Date(week_list_js[right_slider_index]);

        // Set date strings
        document.getElementById("from_span").innerHTML = start_date.toLocaleDateString();
        document.getElementById("to_span").innerHTML = end_date.toLocaleDateString();


        rangeS.forEach(function (el) {
            el.oninput = function () {
                var slide1 = parseFloat(rangeS[0].value),
                    slide2 = parseFloat(rangeS[1].value);

                if (slide1 > slide2) {
                    [slide1, slide2] = [slide2, slide1];

                }
                var start_date = new Date(week_list_js[slide1]);
                var end_date = new Date(week_list_js[slide2]);

                numberS[0].valueAsDate = start_date;
                numberS[1].valueAsDate = end_date;

                document.getElementById("from_span").innerHTML = start_date.toLocaleDateString();
                document.getElementById("to_span").innerHTML = end_date.toLocaleDateString();
            }
        });

        numberS.forEach(function (el) {
            el.oninput = function () {
                var number1 = parseFloat(numberS[0].value),
                    number2 = parseFloat(numberS[1].value);

                if (number1 > number2) {
                    var tmp = number1;
                    numberS[0].value = number2;
                    numberS[1].value = tmp;
                }

                rangeS[0].value = number1;
                rangeS[1].value = number2;

            }
        });

    })();

    function closest_index (num, arr) {
                var curr = arr[0];
                var diff = Math.abs (num - curr);
                for (var val = 0; val < arr.length; val++) {
                    var newdiff = Math.abs (num - arr[val]);
                    if (newdiff < diff) {
                        diff = newdiff;
                        curr = arr[val];
                    }
                }
                return arr.indexOf(curr);
            }