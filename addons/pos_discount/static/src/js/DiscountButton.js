flectra.define('pos_discount.DiscountButton',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constProductScreen=require('point_of_sale.ProductScreen');
    const{useListener}=require('web.custom_hooks');
    constRegistries=require('point_of_sale.Registries');

    classDiscountButtonextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('click',this.onClick);
        }
        asynconClick(){
            varself=this;
            const{confirmed,payload}=awaitthis.showPopup('NumberPopup',{
                title:this.env._t('DiscountPercentage'),
                startingValue:this.env.pos.config.discount_pc,
            });
            if(confirmed){
                constval=Math.max(0,Math.min(100,parseFloat(payload)));
                awaitself.apply_discount(val);
            }
        }

        asyncapply_discount(pc){
            varorder   =this.env.pos.get_order();
            varlines   =order.get_orderlines();
            varproduct =this.env.pos.db.get_product_by_id(this.env.pos.config.discount_product_id[0]);
            if(product===undefined){
                awaitthis.showPopup('ErrorPopup',{
                    title:this.env._t("Nodiscountproductfound"),
                    body :this.env._t("Thediscountproductseemsmisconfigured.Makesureitisflaggedas'CanbeSold'and'AvailableinPointofSale'."),
                });
                return;
            }

            //Removeexistingdiscounts
            vari=0;
            while(i<lines.length){
                if(lines[i].get_product()===product){
                    order.remove_orderline(lines[i]);
                }else{
                    i++;
                }
            }

            //Adddiscount
            //Weaddthepriceasmanuallysettoavoidrecomputationwhenchangingcustomer.
            varbase_to_discount=order.get_total_without_tax();
            if(product.taxes_id.length){
                varfirst_tax=this.env.pos.taxes_by_id[product.taxes_id[0]];
                if(first_tax.price_include){
                    base_to_discount=order.get_total_with_tax();
                }
            }
            vardiscount=-pc/100.0*base_to_discount;

            if(discount<0){
                order.add_product(product,{
                    price:discount,
                    lst_price:discount,
                    extras:{
                        price_manually_set:true,
                    },
                });
            }
        }
    }
    DiscountButton.template='DiscountButton';

    ProductScreen.addControlButton({
        component:DiscountButton,
        condition:function(){
            returnthis.env.pos.config.module_pos_discount&&this.env.pos.config.discount_product_id;
        },
    });

    Registries.Component.add(DiscountButton);

    returnDiscountButton;
});
