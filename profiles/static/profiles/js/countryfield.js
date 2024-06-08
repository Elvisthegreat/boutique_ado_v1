let countrySelected = $('#id_default_country').val(); // Get the value of the selected country and store it in a variable
if(!countrySelected) { // If country not selected, color remains gray
    $('#id_default_country').css('color', '#aab7c4');
};
  // Capture the change event, so whenever the box change we get the value of it
$('#id_default_country').change(function() {
    countrySelected = $(this).val();
    if(!countrySelected) {
        $(this).css('color', '#aab7c4');
    } else {
        $(this).css('color', '#000');
    }
});