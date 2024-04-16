flectra.define('pos_hr.LoginScreen',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    constuseSelectEmployee=require('pos_hr.useSelectEmployee');
    const{useBarcodeReader}=require('point_of_sale.custom_hooks');

    classLoginScreenextendsPosComponent{
        constructor(){
            super(...arguments);
            const{selectEmployee,askPin}=useSelectEmployee();
            this.selectEmployee=selectEmployee;
            this.askPin=askPin;
            useBarcodeReader(
                {
                    cashier:this._barcodeCashierAction,
                },
                true
            );
        }
        back(){
            this.props.resolve({confirmed:false,payload:false});
            this.trigger('close-temp-screen');
        }
        confirm(){
            this.props.resolve({confirmed:true,payload:true});
            this.trigger('close-temp-screen');
        }
        getshopName(){
            returnthis.env.pos.config.name;
        }
        closeSession(){
            this.trigger('close-pos');
        }
        asyncselectCashier(){
            constlist=this.env.pos.employees.map((employee)=>{
                return{
                    id:employee.id,
                    item:employee,
                    label:employee.name,
                    isSelected:false,
                };
            });

            constemployee=awaitthis.selectEmployee(list);
            if(employee){
                this.env.pos.set_cashier(employee);
                this.back();
            }
        }
        async_barcodeCashierAction(code){
            lettheEmployee;
            for(letemployeeofthis.env.pos.employees){
                if(employee.barcode===Sha1.hash(code.code)){
                    theEmployee=employee;
                    break;
                }
            }

            if(!theEmployee)return;

            if(!theEmployee.pin||(awaitthis.askPin(theEmployee))){
                this.env.pos.set_cashier(theEmployee);
                this.back();
            }
        }
    }
    LoginScreen.template='LoginScreen';

    Registries.Component.add(LoginScreen);

    returnLoginScreen;
});
