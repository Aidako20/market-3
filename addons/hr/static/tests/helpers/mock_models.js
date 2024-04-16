flectra.define('hr/static/tests/helpers/mock_models.js',function(require){
'usestrict';

constMockModels=require('mail/static/tests/helpers/mock_models.js');

MockModels.patch('hr/static/tests/helpers/mock_models.js',T=>
    classextendsT{

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *@override
         */
        staticgenerateData(){
            constdata=super.generateData(...arguments);
            Object.assign(data,{
                'hr.employee.public':{
                    fields:{
                        display_name:{string:"Name",type:"char"},
                        user_id:{string:"User",type:"many2one",relation:'res.users'},
                        user_partner_id:{string:"Partner",type:"many2one",relation:'res.partner'},
                    },
                    records:[],
                },
            });
            returndata;
        }

    }
);

});
