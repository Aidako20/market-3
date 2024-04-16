flectra.define('mass_mailing.unsubscribe',function(require){
    'usestrict';

    varsession=require('web.session');
    varajax=require('web.ajax');
    varcore=require('web.core');
    require('web.dom_ready');

    var_t=core._t;

    varemail=$("input[name='email']").val();
    varmailing_id=parseInt($("input[name='mailing_id']").val());
    varres_id=parseInt($("input[name='res_id']").val());
    vartoken=(location.search.split('token'+'=')[1]||'').split('&')[0];

    if(!$('.o_unsubscribe_form').length){
        returnPromise.reject("DOMdoesn'tcontain'.o_unsubscribe_form'");
    }
    session.load_translations().then(function(){
        if(email!=''&&email!=undefined){
            ajax.jsonRpc('/mailing/blacklist/check','call',{'email':email,'mailing_id':mailing_id,'res_id':res_id,'token':token})
                .then(function(result){
                    if(result=='unauthorized'){
                        $('#button_add_blacklist').hide();
                        $('#button_remove_blacklist').hide();
                    }
                    elseif(result==true){
                        $('#button_remove_blacklist').show();
                        toggle_opt_out_section(false);
                    }
                    elseif(result==false){
                        $('#button_add_blacklist').show();
                        toggle_opt_out_section(true);
                    }
                    else{
                        $('#subscription_info').html(_t('Anerroroccured.Pleasetryagainlaterorcontactus.'));
                        $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-warning').addClass('alert-error');
                    }
                })
                .guardedCatch(function(){
                    $('#subscription_info').html(_t('Anerroroccured.Pleasetryagainlaterorcontactus.'));
                    $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-warning').addClass('alert-error');
                });
        }
        else{
            $('#div_blacklist').hide();
        }

        varunsubscribed_list=$("input[name='unsubscribed_list']").val();
        if(unsubscribed_list){
            $('#subscription_info').html(_.str.sprintf(
                _t("Youhavebeen<strong>successfullyunsubscribedfrom%s</strong>."),
                _.escape(unsubscribed_list)
            ));
        }
        else{
            $('#subscription_info').html(_t('Youhavebeen<strong>successfullyunsubscribed</strong>.'));
        }
    });

    $('#unsubscribe_form').on('submit',function(e){
        e.preventDefault();

        varchecked_ids=[];
        $("input[type='checkbox']:checked").each(function(i){
          checked_ids[i]=parseInt($(this).val());
        });

        varunchecked_ids=[];
        $("input[type='checkbox']:not(:checked)").each(function(i){
          unchecked_ids[i]=parseInt($(this).val());
        });

        ajax.jsonRpc('/mail/mailing/unsubscribe','call',{'opt_in_ids':checked_ids,'opt_out_ids':unchecked_ids,'email':email,'mailing_id':mailing_id,'res_id':res_id,'token':token})
            .then(function(result){
                if(result=='unauthorized'){
                    $('#subscription_info').html(_t('Youarenotauthorizedtodothis!'));
                    $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-error').addClass('alert-warning');
                }
                elseif(result==true){
                    $('#subscription_info').html(_t('Yourchangeshavebeensaved.'));
                    $('#info_state').removeClass('alert-info').addClass('alert-success');
                }
                else{
                    $('#subscription_info').html(_t('Anerroroccurred.Yourchangeshavenotbeensaved,tryagainlater.'));
                    $('#info_state').removeClass('alert-info').addClass('alert-warning');
                }
            })
            .guardedCatch(function(){
                $('#subscription_info').html(_t('Anerroroccurred.Yourchangeshavenotbeensaved,tryagainlater.'));
                $('#info_state').removeClass('alert-info').addClass('alert-warning');
            });
    });

    // ==================
    //     Blacklist
    // ==================
    $('#button_add_blacklist').click(function(e){
        e.preventDefault();

        ajax.jsonRpc('/mailing/blacklist/add','call',{'email':email,'mailing_id':mailing_id,'res_id':res_id,'token':token})
            .then(function(result){
                if(result=='unauthorized'){
                    $('#subscription_info').html(_t('Youarenotauthorizedtodothis!'));
                    $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-error').addClass('alert-warning');
                }
                else
                {
                    if(result){
                        $('#subscription_info').html(_t('Youhavebeensuccessfully<strong>addedtoourblacklist</strong>.'
                               +'Youwillnotbecontactedanymorebyourservices.'));
                        $('#info_state').removeClass('alert-warning').removeClass('alert-info').removeClass('alert-error').addClass('alert-success');
                        toggle_opt_out_section(false);
                    }
                    else{
                        $('#subscription_info').html(_t('Anerroroccured.Pleasetryagainlaterorcontactus.'));
                        $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-warning').addClass('alert-error');
                    }
                    $('#button_add_blacklist').hide();
                    $('#button_remove_blacklist').show();
                    $('#unsubscribed_info').hide();
                }
            })
            .guardedCatch(function(){
                $('#subscription_info').html(_t('Anerroroccured.Pleasetryagainlaterorcontactus.'));
                $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-warning').addClass('alert-error');
            });
    });

    $('#button_remove_blacklist').click(function(e){
        e.preventDefault();

        ajax.jsonRpc('/mailing/blacklist/remove','call',{'email':email,'mailing_id':mailing_id,'res_id':res_id,'token':token})
            .then(function(result){
                if(result=='unauthorized'){
                    $('#subscription_info').html(_t('Youarenotauthorizedtodothis!'));
                    $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-error').addClass('alert-warning');
                }
                else
                {
                    if(result){
                        $('#subscription_info').html(_t("Youhavebeensuccessfully<strong>removedfromourblacklist</strong>."
                                +"Youarenowabletobecontactedbyourservices."));
                        $('#info_state').removeClass('alert-warning').removeClass('alert-info').removeClass('alert-error').addClass('alert-success');
                        toggle_opt_out_section(true);
                    }
                    else{
                        $('#subscription_info').html(_t('Anerroroccured.Pleasetryagainlaterorcontactus.'));
                        $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-warning').addClass('alert-error');
                    }
                    $('#button_add_blacklist').show();
                    $('#button_remove_blacklist').hide();
                    $('#unsubscribed_info').hide();
                }
            })
            .guardedCatch(function(){
                $('#subscription_info').html(_t('Anerroroccured.Pleasetryagainlaterorcontactus.'));
                $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-warning').addClass('alert-error');
            });
    });

    //==================
    //     Feedback
    //==================
    $('#button_feedback').click(function(e){
        varfeedback=$("textarea[name='opt_out_feedback']").val();
        e.preventDefault();
        ajax.jsonRpc('/mailing/feedback','call',{'mailing_id':mailing_id,'res_id':res_id,'email':email,'feedback':feedback,'token':token})
            .then(function(result){
                if(result=='unauthorized'){
                    $('#subscription_info').html(_t('Youarenotauthorizedtodothis!'));
                    $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-error').addClass('alert-warning');
                }
                elseif(result==true){
                    $('#subscription_info').html(_t('Thankyou!Yourfeedbackhasbeensentsuccessfully!'));
                    $('#info_state').removeClass('alert-warning').removeClass('alert-info').removeClass('alert-error').addClass('alert-success');
                    $("#div_feedback").hide();
                }
                else{
                    $('#subscription_info').html(_t('Anerroroccured.Pleasetryagainlaterorcontactus.'));
                    $('#info_state').removeClass('alert-success').removeClass('alert-info').removeClass('alert-error').addClass('alert-warning');
                }
            })
            .guardedCatch(function(){
                $('#subscription_info').html(_t('Anerroroccured.Pleasetryagainlaterorcontactus.'));
                $('#info_state').removeClass('alert-info').removeClass('alert-success').removeClass('alert-error').addClass('alert-warning');
            });
    });
});

functiontoggle_opt_out_section(value){
    varresult=!value;
    $("#div_opt_out").find('*').attr('disabled',result);
    $("#button_add_blacklist").attr('disabled',false);
    $("#button_remove_blacklist").attr('disabled',false);
    if(value){$('[name="button_subscription"]').addClass('clickable'); }
    else{$('[name="button_subscription"]').removeClass('clickable');}
}
