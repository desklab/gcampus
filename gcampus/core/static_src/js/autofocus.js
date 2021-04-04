let autofocusFields = document.querySelectorAll('.autofocus');
let autofocusCount = autofocusFields.length;
autofocusFields.forEach((element, i) => {
    element.oninput = function(event) {
        if (element.value.length > element.maxLength)
            element.value = String(element.value).slice(0, element.maxLength);
        if (element.value.length >= element.maxLength && (i + 1) < autofocusCount)
            autofocusFields[i + 1].focus(function() { this.select(); } );
    };
});
