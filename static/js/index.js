+ function($) {
    $('.palceholder').click(function() {
      $(this).siblings('input').focus();
    });
  
    $('.form-control').focus(function() {
      $(this).parent().addClass("focused");
    });
  
    $('.form-control').blur(function() {
      var $this = $(this);
      if ($this.val().length == 0)
        $(this).parent().removeClass("focused");
    });
    $('.form-control').blur();


    $('.form-select').focus(function() {
        $(this).parent().addClass("focused");
      });
    
      $('.form-select').blur(function() {
        var $this = $(this);
        if ($this.val().length == 0)
          $(this).parent().removeClass("focused");
      });
      $('.form-select').blur();
  
    // validetion
    $.validator.setDefaults({
      errorElement: 'span',
      errorClass: 'validate-tooltip'
    });
  
    $("#formvalidate").validate({
      rules: {
        RFR_value: {
          required: true
        },
        currency: {
          required: true
        },
        obs_date: {
            required: true
          }
      },
      messages: {
        RFR_value: {
          required: "Sorry! This parameter is mandatory."
        },
        currency: {
          required: "Sorry! This parameter is mandatory."
        },
        obs_date: {
            required: "Sorry! This parameter is mandatory."
        },
    }
    });
  
  }(jQuery);