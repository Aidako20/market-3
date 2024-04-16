flectra.define('l10n_gcc_pos.OrderReceipt',function(require){
    'usestrict';

    constOrderReceipt=require('point_of_sale.OrderReceipt')
    constRegistries=require('point_of_sale.Registries');

    constOrderReceiptGCC=OrderReceipt=>
        classextendsOrderReceipt{

            getreceiptEnv(){
                letreceipt_render_env=super.receiptEnv;
                letreceipt=receipt_render_env.receipt;
                letcompany=this.env.pos.company;
                receipt.is_gcc_country=company.country?['SA','AE','BH','OM','QA','KW'].includes(company.country.code):false;
                returnreceipt_render_env;
            }
        }
    Registries.Component.extend(OrderReceipt,OrderReceiptGCC)
    returnOrderReceiptGCC
});
