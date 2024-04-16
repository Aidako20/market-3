flectra.define('website_blog.s_latest_posts_editor',function(require){
'usestrict';

varsOptions=require('web_editor.snippets.options');
varwUtils=require('website.utils');

sOptions.registry.js_get_posts_selectBlog=sOptions.Class.extend({

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _renderCustomXML:function(uiFragment){
        returnthis._rpc({
            model:'blog.blog',
            method:'search_read',
            args:[wUtils.websiteDomain(this),['name']],
        }).then(blogs=>{
            constmenuEl=uiFragment.querySelector('[name="blog_selection"]');
            for(constblogofblogs){
                constel=document.createElement('we-button');
                el.dataset.selectDataAttribute=blog.id;
                el.textContent=blog.name;
                menuEl.appendChild(el);
            }
        });
    },
});
});
