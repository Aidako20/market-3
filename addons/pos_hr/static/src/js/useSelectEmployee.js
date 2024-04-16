flectra.define('pos_hr.useSelectEmployee',function(require){
    'usestrict';

    const{Component}=owl;

    functionuseSelectEmployee(){
        constcurrent=Component.current;

        asyncfunctionaskPin(employee){
            const{confirmed,payload:inputPin}=awaitthis.showPopup('NumberPopup',{
                isPassword:true,
                title:this.env._t('Password?'),
                startingValue:null,
            });

            if(!confirmed)returnfalse;

            if(employee.pin===Sha1.hash(inputPin)){
                returnemployee;
            }else{
                awaitthis.showPopup('ErrorPopup',{
                    title:this.env._t('IncorrectPassword'),
                });
                returnfalse;
            }
        }

        asyncfunctionselectEmployee(selectionList){
            const{confirmed,payload:employee}=awaitthis.showPopup('SelectionPopup',{
                title:this.env._t('ChangeCashier'),
                list:selectionList,
            });

            if(!confirmed)returnfalse;

            if(!employee.pin){
                returnemployee;
            }

            returnawaitaskPin.call(current,employee);
        }
        return{askPin:askPin.bind(current),selectEmployee:selectEmployee.bind(current)};
    }

    returnuseSelectEmployee;
});
