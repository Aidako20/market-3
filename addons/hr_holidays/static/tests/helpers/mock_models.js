flectra.define('hr_holidays/static/tests/helpers/mock_models.js',function(require){
'usestrict';

constMockModels=require('mail/static/tests/helpers/mock_models.js');

MockModels.patch('hr_holidays/static/tests/helpers/mock_models.js',T=>
    classextendsT{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *@override
         */
        staticgenerateData(){
            constdata=super.generateData(...arguments);
            Object.assign(data['res.partner'].fields,{
                //Notarealfieldbuteasethetesting
                out_of_office_date_end:{type:'datetime'},
            });
            returndata;
        }

    }
);

});
