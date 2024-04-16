flectra.define('pos_hr.CashierName',function(require){
    'usestrict';

    constCashierName=require('point_of_sale.CashierName');
    constRegistries=require('point_of_sale.Registries');
    constuseSelectEmployee=require('pos_hr.useSelectEmployee');
    const{useBarcodeReader}=require('point_of_sale.custom_hooks');

    constPosHrCashierName=(CashierName)=>
        classextendsCashierName{
            constructor(){
                super(...arguments);
                const{selectEmployee,askPin}=useSelectEmployee();
                this.askPin=askPin;
                this.selectEmployee=selectEmployee;
                useBarcodeReader({cashier:this._onCashierScan});
            }
            mounted(){
                this.env.pos.on('change:cashier',this.render,this);
            }
            willUnmount(){
                this.env.pos.off('change:cashier',null,this);
            }
            asyncselectCashier(){
                if(!this.env.pos.config.module_pos_hr)return;

                constlist=this.env.pos.employees
                    .filter((employee)=>employee.id!==this.env.pos.get_cashier().id)
                    .map((employee)=>{
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
                }
            }
            async_onCashierScan(code){
                constemployee=this.env.pos.employees.find(
                    (emp)=>emp.barcode===Sha1.hash(code.code)
                );

                if(!employee||employee===this.env.pos.get_cashier())return;

                if(!employee.pin||(awaitthis.askPin(employee))){
                    this.env.pos.set_cashier(employee);
                }
            }
        };

    Registries.Component.extend(CashierName,PosHrCashierName);

    returnCashierName;
});
