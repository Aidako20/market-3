    $(function(){
        "usestrict";
        //mergedHeadwillbeturnedtotruethefirsttimewereceivesomethingfromanewhost
        //Itallowstotransformthe<head>onlyonce
        varmergedHead=false;
        varcurrent_client_url="";

        functionlongpolling(){
            $.ajax({
                type:'POST',
                url:window.location.origin+'/point_of_sale/get_serialized_order/'+display_identifier,
                dataType:'json',
                beforeSend:function(xhr){xhr.setRequestHeader('Content-Type','application/json');},
                data:JSON.stringify({jsonrpc:'2.0'}),

                success:function(data){
                    if(data.result.error){
                        $('.error-message').text(data.result.error);
                        $('.error-message').removeClass('d-none');
                        setTimeout(longpolling,5000);
                        return;
                    }
                    if(data.result.rendered_html){
                        vartrimmed=$.trim(data.result.rendered_html);
                        var$parsedHTML=$('<div>').html($.parseHTML(trimmed,true));//WARNING:thetrueherewillexecutesanyscriptpresentinthestringtoparse
                        varnew_client_url=$parsedHTML.find(".resources>base").attr('href');

                        if(!mergedHead||(current_client_url!==new_client_url)){

                            mergedHead=true;
                            current_client_url=new_client_url;
                            $("head").children().not('.origin').remove();
                            $("head").append($parsedHTML.find(".resources").html());
                        }

                        $(".container-fluid").html($parsedHTML.find('.pos-customer_facing_display').html());
                        $(".container-fluid").attr('class','container-fluid').addClass($parsedHTML.find('.pos-customer_facing_display').attr('class'));

                        vard=$('.pos_orderlines_list');
                        d.scrollTop(d.prop("scrollHeight"));

                        //Hereweexecutethecodecomingfromthepos,apparently$.parseHTML()executesscriptsrightaway,
                        //Sincewemodifythedomafterwards,thescriptmightnothaveanyeffect
                        if(typeofforeign_js!=='undefined'&&$.isFunction(foreign_js)){
                            foreign_js();
                        }
                    }
                    longpolling();
                },

                error:function(jqXHR,status,err){
                    setTimeout(longpolling,5000);
                },

                timeout:30000,
            });
        };

        longpolling();
    });
