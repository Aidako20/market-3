flectra.define('point_of_sale.CashBoxOpening',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    const{Gui}=require('point_of_sale.Gui');
    constfield_utils=require('web.field_utils');

    classCashBoxOpeningextendsPosComponent{
        constructor(){
            super(...arguments);
            this.changes={};
            this.defaultValue=this.env.pos.format_currency_no_symbol(
                this.env.pos.bank_statement.balance_start||0
            );
            this.symbol=this.env.pos.currency.symbol;
        }
        captureChange(event){
            this.changes[event.target.name]=event.target.value;
        }
        startSession(){
            letcashOpening=this.changes.cashBoxValue?this.changes.cashBoxValue:this.defaultValue;
            try{
               cashOpening=field_utils.parse.float(cashOpening);
            }catch(err){
                cashOpening=NaN;
            }
            if(isNaN(cashOpening)){
                Gui.showPopup('ErrorPopup',{
                    'title':'Wrongvalue',
                    'body': 'Pleaseinsertacorrectvalue.',
                });
                return;
            }
            this.env.pos.bank_statement.balance_start=cashOpening;
            this.env.pos.pos_session.state='opened';
            this.props.cashControl.cashControl=false;
            this.rpc({
                    model:'pos.session',
                    method:'set_cashbox_pos',
                    args:[this.env.pos.pos_session.id,cashOpening,this.changes.notes],
                });
        }
    }
    CashBoxOpening.template='CashBoxOpening';

    Registries.Component.add(CashBoxOpening);

    returnCashBoxOpening;
});
