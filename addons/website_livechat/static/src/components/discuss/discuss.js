flectra.define('website_livechat/static/src/components/discuss/discuss.js',function(require){
'usestrict';

constcomponents={
    Discuss:require('mail/static/src/components/discuss/discuss.js'),
    VisitorBanner:require('website_livechat/static/src/components/visitor_banner/visitor_banner.js'),
};

components.Discuss.patch('website_livechat/static/src/components/discuss/discuss.js',T=>
    classextendsT{

        /**
         *@override
         */
        _useStoreSelector(props){
            constres=super._useStoreSelector(...arguments);
            constthread=res.thread;
            constvisitor=thread&&thread.visitor;
            returnObject.assign({},res,{
                visitor,
            });
        }

    }
);

Object.assign(components.Discuss.components,{
    VisitorBanner:components.VisitorBanner,
});

});
