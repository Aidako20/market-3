flectra.define('website_sale.utils',function(require){
'usestrict';

functionanimateClone($cart,$elem,offsetTop,offsetLeft){
    if(!$cart.length){
        returnPromise.resolve();
    }
    $cart.find('.o_animate_blink').addClass('o_red_highlighto_shadow_animation').delay(500).queue(function(){
        $(this).removeClass("o_shadow_animation").dequeue();
    }).delay(2000).queue(function(){
        $(this).removeClass("o_red_highlight").dequeue();
    });
    returnnewPromise(function(resolve,reject){
        var$imgtodrag=$elem.find('img').eq(0);
        if($imgtodrag.length){
            var$imgclone=$imgtodrag.clone()
                .offset({
                    top:$imgtodrag.offset().top,
                    left:$imgtodrag.offset().left
                })
                .addClass('o_website_sale_animate')
                .appendTo(document.body)
                .animate({
                    top:$cart.offset().top+offsetTop,
                    left:$cart.offset().left+offsetLeft,
                    width:75,
                    height:75,
                },1000,'easeInOutExpo');

            $imgclone.animate({
                width:0,
                height:0,
            },function(){
                resolve();
                $(this).detach();
            });
        }else{
            resolve();
        }
    });
}

/**
 *Updatesbothnavbarcart
 *@param{Object}data
 */
functionupdateCartNavBar(data){
    $(".my_cart_quantity")
        .parents('li.o_wsale_my_cart').removeClass('d-none').end()
        .toggleClass('fafa-warning',!data.cart_quantity)
        .attr('title',data.warning)
        .text(data.cart_quantity||'')
        .hide()
        .fadeIn(600);

    $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();
    $(".js_cart_summary").first().before(data['website_sale.short_cart_summary']).end().remove();
}

/**
 *Displays`message`inanalertboxatthetopofthepageifit'sa
 *non-emptystring.
 *
 *@param{string|null}message
 */
functionshowWarning(message){
    if(!message){
        return;
    }
    var$page=$('.oe_website_sale');
    varcart_alert=$page.children('#data_warning');
    if(!cart_alert.length){
        cart_alert=$(
            '<divclass="alertalert-dangeralert-dismissible"role="alert"id="data_warning">'+
                '<buttontype="button"class="close"data-dismiss="alert">&times;</button>'+
                '<span></span>'+
            '</div>').prependTo($page);
    }
    cart_alert.children('span:last-child').text(message);
}

return{
    animateClone:animateClone,
    updateCartNavBar:updateCartNavBar,
    showWarning:showWarning,
};
});
