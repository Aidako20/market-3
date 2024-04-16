$(function(){

    $('input#cc_number').payment('formatCardNumber');
    $('input#cc_cvc').payment('formatCardCVC');
    $('input#cc_expiry').payment('formatCardExpiry')

    $('input#cc_number').on('focusout',function(e){
        varvalid_value=$.payment.validateCardNumber(this.value);
        varcard_type=$.payment.cardType(this.value);
        if(card_type){
            $(this).parent('.form-group').children('.card_placeholder').removeClass().addClass('card_placeholder'+card_type);
            $(this).parent('.form-group').children('input[name="cc_brand"]').val(card_type)
        }
        else{
            $(this).parent('.form-group').children('.card_placeholder').removeClass().addClass('card_placeholder');
        }
        if(valid_value){
            $(this).parent('.form-group').addClass('o_has_success').find('.form-control,.custom-select').addClass('is-valid');
            $(this).parent('.form-group').removeClass('o_has_error').find('.form-control,.custom-select').removeClass('is-invalid');
            $(this).siblings('.o_invalid_field').remove();
        }
        else{
            $(this).parent('.form-group').addClass('o_has_error').find('.form-control,.custom-select').addClass('is-invalid');
            $(this).parent('.form-group').removeClass('o_has_success').find('.form-control,.custom-select').removeClass('is-valid');
        }
    });

    $('input#cc_cvc').on('focusout',function(e){
        varcc_nbr=$(this).parents('.oe_cc').find('#cc_number').val();
        varcard_type=$.payment.cardType(cc_nbr);
        varvalid_value=$.payment.validateCardCVC(this.value,card_type);
        if(valid_value){
            $(this).parent('.form-group').addClass('o_has_success').find('.form-control,.custom-select').addClass('is-valid');
            $(this).parent('.form-group').removeClass('o_has_error').find('.form-control,.custom-select').removeClass('is-invalid');
            $(this).siblings('.o_invalid_field').remove();
        }
        else{
            $(this).parent('.form-group').addClass('o_has_error').find('.form-control,.custom-select').addClass('is-invalid');
            $(this).parent('.form-group').removeClass('o_has_success').find('.form-control,.custom-select').removeClass('is-valid');
        }
    });

    $('input#cc_expiry').on('focusout',function(e){
        varexpiry_value=$.payment.cardExpiryVal(this.value);
        varmonth=expiry_value.month||'';
        varyear=expiry_value.year||'';
        varvalid_value=$.payment.validateCardExpiry(month,year);
        if(valid_value){
            $(this).parent('.form-group').addClass('o_has_success').find('.form-control,.custom-select').addClass('is-valid');
            $(this).parent('.form-group').removeClass('o_has_error').find('.form-control,.custom-select').removeClass('is-invalid');
            $(this).siblings('.o_invalid_field').remove();
        }
        else{
            $(this).parent('.form-group').addClass('o_has_error').find('.form-control,.custom-select').addClass('is-invalid');
            $(this).parent('.form-group').removeClass('o_has_success').find('.form-control,.custom-select').removeClass('is-valid');
        }
    });

    $('select[name="pm_acquirer_id"]').on('change',function(){
        varacquirer_id=$(this).val();
        $('.acquirer').addClass('d-none');
        $('.acquirer[data-acquirer-id="'+acquirer_id+'"]').removeClass('d-none');
    });

});
