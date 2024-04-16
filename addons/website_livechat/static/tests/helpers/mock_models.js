flectra.define('website_livechat/static/tests/helpers/mock_models.js',function(require){
'usestrict';

constMockModels=require('mail/static/tests/helpers/mock_models.js');

MockModels.patch('website_livechat/static/tests/helpers/mock_models.js',T=>
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
                'website.visitor':{
                    fields:{
                        country_id:{string:"Country",type:'many2one',relation:'res.country'},
                        display_name:{string:"Displayname",type:'string'},
                        //Representthebrowsinghistoryofthevisitorasastring.
                        //Toeasetestingthisallowsteststosetitdirectlyinstead
                        //ofimplementingthecomputationmadeonserver.
                        //Thisshouldnormallynotbeafield.
                        history:{string:"History",type:'string'},
                        is_connected:{string:"Isconnected",type:'boolean'},
                        lang:{string:"Language",type:'string'},
                        partner_id:{string:"partner",type:"many2one",relation:'res.partner'},
                        website:{string:"Website",type:'string'},
                    },
                    records:[],
                },
            });
            Object.assign(data['mail.channel'].fields,{
                livechat_visitor_id:{string:"Visitor",type:'many2one',relation:'website.visitor'},
            });
            returndata;
        }

    }
);

});
